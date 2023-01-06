from odoo import api, fields, models, _
from datetime import date, datetime, timedelta


class PaymentStatusReportTemplate(models.AbstractModel):
    _name = 'report.payment_process_reports_baykee.payment_status_report'
    _description = 'Payment Status Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['payment.status.wiz'].browse(docids[0])
        company_id = self.env.user.company_id
        analytic_account = docs.analytic_account_id.ids if docs.analytic_account_id else []
        division = docs.division_id.ids if docs.division_id else []
        payment_mode = docs.payment_mode.id if docs.payment_mode else []
        temp = []
        domain = [('create_date', '>=', docs.start_date), ('create_date', '<=', docs.end_date)]
        if docs.state:
            domain.append(('state', '=', docs.state))
        if division:
            domain.append(('division', 'in', division))
        if analytic_account:
            domain.append(('account_analytic_id', 'in', analytic_account))
        if payment_mode:
            domain.append(('payment_mode', 'in', payment_mode))
        payment_process = self.env['payment.process'].search(domain)
        for payment in payment_process:
            vals = {
                'ref': payment.name,
                'term': payment.term,
                'desc': payment.purpose,
                'status': payment.payment_status,
                'amount': payment.amount,
            }
            temp.append(vals)
            print(temp)
        temp2 = temp
        data_temp.append([temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
