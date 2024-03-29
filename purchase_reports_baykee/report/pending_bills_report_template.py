from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PendingBillsReportTemplate(models.AbstractModel):
    _name = 'report.purchase_reports_baykee.pending_bills_report_temp'
    _description = 'Pending Bills Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['pending.bills.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        temp = []
        domain = [('date_order', '>=', start_date), ('date_order', '<=', end_date),
                  ('invoice_status', '=', 'to invoice')]
        purchase_order = self.env['purchase.order'].search(domain).sorted(key=lambda r: r.partner_id)
        for order in purchase_order:
            vals = {
                'ref': order.name,
                'confirm_date': order.date_approve,
                'vendor': order.partner_id.name,
                'receipt_date': order.date_planned,
                'represent': order.user_id.name,
                'total': order.amount_total,
                'billing_status': order.invoice_status,
            }
            temp.append(vals)
        temp2 = temp
        data_temp.append(
            [temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
