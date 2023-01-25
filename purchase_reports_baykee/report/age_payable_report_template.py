from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AgePayableTemplate(models.AbstractModel):
    _name = 'report.purchase_reports_baykee.age_payable_temp'
    _description = 'Age Payable Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['age.payable.report'].browse(docids[0])
        date = docs.date
        partners = docs.partner_id.ids if docs.partner_id else []
        analytic_accounts = docs.analytic_account_id.ids if docs.analytic_account_id else []
        analytic_tags = docs.analytic_tag_id.ids if docs.analytic_tag_id else []
        data_temp = []
        part_domain = []
        if partners:
            part_domain += [('id', 'in', partners)]
        partner_search = self.env['res.partner'].search(part_domain)
        for partner in partner_search:
            temp1 = []
            payment_domain = [('date', '<=', date),
                              ('partner_id', '=', partner.id),
                              ('state', '=', 'posted'),
                              ('payment_type', '=', 'outbound'),
                              ('is_reconciled', '=', False),
                              ('partner_id.property_account_payable_id', '=',
                               partner.property_account_payable_id.id)]
            payments = self.env['account.payment'].search(payment_domain)
            for payment in payments:
                as_of = 0
                a = 0
                b = 0
                c = 0
                d = 0
                e = 0
                delta = date - payment.date
                days = delta.days
                if 0 <= days < 1:
                    as_of = payment.amount
                elif days <= 30:
                    a = payment.amount
                elif 31 <= days <= 60:
                    b = payment.amount
                elif 61 <= days <= 90:
                    c = payment.amount
                elif 91 <= days <= 120:
                    d = payment.amount
                elif days >= 121:
                    e = payment.amount
                vals = {
                    'name': payment.name,
                    'due_date': payment.date,
                    'account': partner.property_account_payable_id.name,
                    'as_data': -as_of,
                    '1-30': -a,
                    '31-60': -b,
                    '61-90': -c,
                    '91-120': -d,
                    'older': -e,
                    'total': False,
                }
                temp1.append(vals)
            temp = []
            domain = [('invoice_date', '<=', date),
                      ('partner_id', '=', partner.id),
                      ('payment_state', '=', 'not_paid'),
                      ('state', '=', 'posted'),
                      ('move_type', '=', ['in_invoice', 'in_refund']),
                      ('partner_id.property_account_payable_id', '=', partner.property_account_payable_id.id)]
            if analytic_accounts:
                domain.append(('analytic_account_id', '=', analytic_accounts))
            if analytic_tags:
                domain.append(('analytic_tag_ids', '=', analytic_tags))
            data_complete = self.env['account.move'].search(domain)
            print(data_complete)
            for line in data_complete:
                as_of = 0
                a = 0
                b = 0
                c = 0
                d = 0
                e = 0
                delta = date - line.invoice_date_due
                days = delta.days
                if 0 <= days < 1:
                    as_of = line.amount_total
                elif days <= 30:
                    a = line.amount_total
                elif 31 <= days <= 60:
                    b = line.amount_total
                elif 61 <= days <= 90:
                    c = line.amount_total
                elif 91 <= days <= 120:
                    d = line.amount_total
                elif days >= 121:
                    e = line.amount_total
                vals = {
                    'name': line.name,
                    'due_date': line.invoice_date_due,
                    'account': partner.property_account_payable_id.name,
                    'as_data': as_of,
                    '1-30': a,
                    '31-60': b,
                    '61-90': c,
                    '91-120': d,
                    'older': e,
                    'total': False,
                }
                temp.append(vals)
            temp2 = temp + temp1
            data_temp.append(
                [partner.name, temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'account.move',
            'analytic_accounts': docs.analytic_account_id,
            'analytic_accounts_all': "All",
            'analytic_tags': docs.analytic_tag_id,
            'analytic_tags_all': "All",
            'dat': data_temp,
            'data': data,
            'docs': docs
        }
