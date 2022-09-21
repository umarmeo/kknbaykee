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
        analytic_account = docs.analytic_account_id if docs.analytic_account_id else []
        sp_domain = []
        sale_person_list = []
        for sp in sale_person:
            sale_person_list.append(sp.id)
        if sale_person_list:
            sp_domain += [('id', 'in', sale_person_list)]
        sale_person_search = self.env['res.users'].search(sp_domain)
        print(sale_person_search, 'sale_person_search')
        for person in sale_person_search:
            temp = []
            domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                      ('user_id', '=', person.id)]
            if analytic_account:
                domain.append(('analytic_account_id', '=', analytic_account))
            sale_order = self.env['sale.order'].search(domain).sorted(key=lambda r: r.user_id)
            for order in sale_order:
                invoices = self.env['account.move'].search([('invoice_origin', '=', order.name)])
                if len(invoices) > 0:
                    for inv in invoices:
                        vals = {
                            'sale_order': order.name,
                            'invoice': inv.name,
                            'customer': order.partner_id.name,
                            'amount_nogst': order.amount_untaxed,
                            'gst': order.amount_tax,
                            'amount_gst': order.amount_total,
                        }
                        temp.append(vals)
                else:
                    vals = {
                        'sale_order': order.name,
                        'invoice': False,
                        'customer': order.partner_id.name,
                        'amount_nogst': order.amount_untaxed,
                        'gst': order.amount_tax,
                        'amount_gst': order.amount_total,
                    }
                    temp.append(vals)
            temp2 = temp
            data_temp.append(
                [person.name, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'sale.order',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
