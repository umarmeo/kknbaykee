from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SalePersonWiseSaleReportTemplate(models.AbstractModel):
    _name = 'report.sale_reports_baykee.sale_person_wise_sale_temp'
    _description = 'Sale Person Wise Sale Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):

        data_temp = []
        docs = self.env['sale.person.wise.sale.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        sale_person = docs.sale_person
        sale_team = docs.sale_team
        analytic_account = docs.analytic_account_id.ids
        analytic_tags = docs.analytic_tag_id.ids
        if docs.report_type == 'sale_person':
            person_domain = []
            if sale_person:
                person_domain += [('id', 'in', sale_person)]
            sale_person_search = self.env['res.users'].search(person_domain)
            for person in sale_person_search:
                temp = []
                domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                          ('user_id', '=', person.id), ('state', '=', 'sale')]
                sale_order = self.env['sale.order'].search(domain).sorted(key=lambda r: r.user_id)
                for order in sale_order:
                    invoices = self.env['account.move'].search(
                        [('invoice_origin', '=', order.name), ('state', '=', 'posted'),
                         ('ref', 'not ilike', 'Reversal of')])
                    vals = {
                        'sale_order': order.name,
                        'invoice': invoices.name,
                        'customer': order.partner_id.name,
                        'amount_nogst': order.amount_untaxed,
                        'gst': order.amount_tax,
                        'amount_gst': order.amount_total,
                    }
                    if invoices:
                        temp.append(vals)
                temp2 = temp
                data_temp.append(
                    [person.name, temp2, start_date, end_date])
        if docs.report_type == 'sale_team':
            team_domain = []
            if sale_team:
                team_domain += [('id', 'in', sale_team)]
            sale_team_search = self.env['crm.team'].search(team_domain)
            for team in sale_team_search:
                temp = []
                domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                          ('team_id', '=', team.id), ('state', '=', 'sale')]
                sale_order = self.env['sale.order'].search(domain).sorted(key=lambda r: r.user_id)
                for order in sale_order:
                    invoices = self.env['account.move'].search(
                        [('invoice_origin', '=', order.name), ('state', '=', 'posted'),
                         ('ref', 'not ilike', 'Reversal of')])
                    vals = {
                        'sale_order': order.name,
                        'invoice': invoices.name,
                        'customer': order.partner_id.name,
                        'amount_nogst': order.amount_untaxed,
                        'gst': order.amount_tax,
                        'amount_gst': order.amount_total,
                    }
                    if invoices:
                        temp.append(vals)
                temp2 = temp
                data_temp.append(
                    [team.name, temp2, start_date, end_date])
        if docs.report_type == 'sale_project':
            account_domain = []
            if analytic_account:
                account_domain += [('id', 'in', analytic_account)]
            analytic_account_search = self.env['account.analytic.account'].search(account_domain)
            for account in analytic_account_search:
                temp = []
                domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                          ('analytic_account_id', '=', account.id), ('state', '=', 'sale')]
                sale_order = self.env['sale.order'].search(domain).sorted(key=lambda r: r.user_id)
                for order in sale_order:
                    invoices = self.env['account.move'].search(
                        [('invoice_origin', '=', order.name), ('state', '=', 'posted'),
                         ('ref', 'not ilike', 'Reversal of')])
                    vals = {
                        'sale_order': order.name,
                        'invoice': invoices.name,
                        'customer': order.partner_id.name,
                        'division': order.analytic_tag_ids.name,
                        'amount_nogst': order.amount_untaxed,
                        'gst': order.amount_tax,
                        'amount_gst': order.amount_total,
                    }
                    if invoices:
                        temp.append(vals)
                temp2 = temp
                data_temp.append(
                    [account.name, temp2, start_date, end_date])
        if docs.report_type == 'sale_division':
            tag_domain = []
            if analytic_tags:
                tag_domain += [('id', 'in', analytic_tags)]
            analytic_tag_search = self.env['account.analytic.tag'].search(tag_domain)
            for tag in analytic_tag_search:
                temp = []
                domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                          ('analytic_tag_ids', '=', tag.id), ('state', '=', 'sale')]
                sale_order = self.env['sale.order'].search(domain).sorted(key=lambda r: r.user_id)
                for order in sale_order:
                    invoices = self.env['account.move'].search(
                        [('invoice_origin', '=', order.name), ('state', '=', 'posted'),
                         ('ref', 'not ilike', 'Reversal of')])
                    vals = {
                        'sale_order': order.name,
                        'invoice': invoices.name,
                        'customer': order.partner_id.name,
                        'project': order.analytic_account_id.name,
                        'amount_nogst': order.amount_untaxed,
                        'gst': order.amount_tax,
                        'amount_gst': order.amount_total,
                    }
                    if invoices:
                        temp.append(vals)
                temp2 = temp
                data_temp.append(
                    [tag.name, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'sale.order',
            'dat': data_temp,
            'docs': docs,
            'analytic_account': docs.analytic_account_id,
            'analytic_account_all': "All",
            'analytic_tag': docs.analytic_tag_id,
            'analytic_tag_all': "All",
            'company_id': company_id,
            'data': data,
        }
