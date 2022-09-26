# -*- coding: utf-8 -*-
import re

from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.osv.expression import AND, expression


class PurchaseReport(models.Model):

    _inherit = 'purchase.report'
    _description = "Purchase Report Customization"

    account_analytic_tag_id = fields.Many2one('account.analytic.tag', string='Analytic Tags', readonly=True)


    @property
    def _table_query(self):
        ''' Report needs to be dynamic to take into account multi-company selected + multi-currency rates '''
        return '%s %s %s' % (self._select(), self._from(), self._group_by())

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
                SELECT
                    po.id as order_id,
                    min(l.id) as id,
                    po.date_order as date_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_id as partner_id,
                    po.user_id as user_id,
                    po.company_id as company_id,
                    po.fiscal_position_id as fiscal_position_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    po.currency_id,
                    t.uom_id as product_uom,
                    extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as price_total,
                    (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) * currency_table.rate as price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    analytic_account.id as account_analytic_id,
                    analytic_tag.id as account_analytic_tag_id,
                    sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
                    sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
                    sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) * currency_table.rate as untaxed_total,
                    sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
                    sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
                    sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
                    case when t.purchase_method = 'purchase' 
                         then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                         else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                    end as qty_to_be_billed
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
            FROM
            purchase_order_line l
                join purchase_order po on (l.order_id=po.id)
                join res_partner partner on po.partner_id = partner.id
                    left join product_product p on (l.product_id=p.id)
                        left join product_template t on (p.product_tmpl_id=t.id)
                left join uom_uom line_uom on (line_uom.id=l.product_uom)
                left join uom_uom product_uom on (product_uom.id=t.uom_id)
                left join account_analytic_account analytic_account on (l.account_analytic_id = analytic_account.id)
                left join account_analytic_tag analytic_tag on (l.analytic_tag_ids = analytic_tag.id)
                left join currency_rate cr on (cr.currency_id = po.currency_id and
                    cr.company_id = po.company_id and
                    cr.date_start <= coalesce(po.date_order, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(po.date_order, now())))
                left join {currency_table} ON currency_table.company_id = po.company_id
        """.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
        )
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                po.company_id,
                po.user_id,
                po.partner_id,
                line_uom.factor,
                po.currency_id,
                l.price_unit,
                po.date_approve,
                l.date_planned,
                l.product_uom,
                po.dest_address_id,
                po.fiscal_position_id,
                l.product_id,
                p.product_tmpl_id,
                t.categ_id,
                po.date_order,
                po.state,
                line_uom.uom_type,
                line_uom.category_id,
                t.uom_id,
                t.purchase_method,
                line_uom.id,
                product_uom.factor,
                partner.country_id,
                partner.commercial_partner_id,
                analytic_account.id,
                analytic_tag.id,
                po.id,
                currency_table.rate
        """
        return group_by_str

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This is a hack to allow us to correctly calculate the average of PO specific date values since
            the normal report query result will duplicate PO values across its PO lines during joins and
            lead to incorrect aggregation values.

            Only the AVG operator is supported for avg_days_to_purchase.
        """
        avg_days_to_purchase = next((field for field in fields if re.search(r'\bavg_days_to_purchase\b', field)), False)

        if avg_days_to_purchase:
            fields.remove(avg_days_to_purchase)
            if any(field.split(':')[1].split('(')[0] != 'avg' for field in [avg_days_to_purchase] if field):
                raise UserError("Value: 'avg_days_to_purchase' should only be used to show an average. If you are seeing this message then it is being accessed incorrectly.")

        res = []
        if fields:
            res = super(PurchaseReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        if not res and avg_days_to_purchase:
            res = [{}]

        if avg_days_to_purchase:
            self.check_access_rights('read')
            query = """ SELECT AVG(days_to_purchase.po_days_to_purchase)::decimal(16,2) AS avg_days_to_purchase
                          FROM (
                              SELECT extract(epoch from age(po.date_approve,po.create_date))/(24*60*60) AS po_days_to_purchase
                              FROM purchase_order po
                              WHERE po.id IN (
                                  SELECT "purchase_report"."order_id" FROM %s WHERE %s)
                              ) AS days_to_purchase
                    """

            subdomain = AND([domain, [('company_id', '=', self.env.company.id), ('date_approve', '!=', False)]])
            subtables, subwhere, subparams = expression(subdomain, self).query.get_sql()

            self.env.cr.execute(query % (subtables, subwhere), subparams)
            res[0].update({
                '__count': 1,
                avg_days_to_purchase.split(':')[0]: self.env.cr.fetchall()[0][0],
            })
        return res
