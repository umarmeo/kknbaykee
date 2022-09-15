from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CashAndBankSummaryTemplate(models.AbstractModel):
    _name = 'report.accounting_reports_baykee.cash_bank_summary_temp'
    _description = 'Cash and Bank Summary Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['cash.bank.summary.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        fold = docs.fold
        post = docs.posted
        main = []
        account_type = self.env['account.account.type'].search([('name', '=', 'Bank and Cash')])
        chart_of_account = self.env['account.account'].search([('user_type_id.name', '=', account_type.name)])
        for chart in chart_of_account:
            if post == '0':
                open_balance = self.env['account.move.line'].search(
                    [('date', '<', start_date), ('account_id', '=', chart.id), ('move_id.state', '=', 'posted')])
            else:
                open_balance = self.env['account.move.line'].search(
                    [('date', '<', start_date), ('account_id', '=', chart.id)])
            open_bal = 0
            for op in open_balance:
                open_bal += op.balance
            if fold == '1':
                main.append({
                    'account': chart.code + ' ' + chart.name,
                    'open_bal': open_bal,
                    'narration': False,
                    'receipt': False,
                    'payment': False,
                    'close_bal': open_bal,
                })
                if post == '0':
                    move_lines = self.env['account.move.line'].search(
                        [('date', '>=', start_date), ('date', '<=', end_date),
                         ('account_id', '=', chart.id), ('move_id.state', '=', 'posted')], order='id')
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('date', '>=', start_date), ('date', '<=', end_date),
                         ('account_id', '=', chart.id)], order='id')
                for line in move_lines:
                    open_bal += line.balance
                    main.append({
                        'account': False,
                        'open_bal': False,
                        'narration': line.name,
                        'receipt': line.debit,
                        'payment': line.credit,
                        'close_bal': open_bal,
                    })
            if fold == '0':
                debit = 0
                credit = 0
                close_bal = 0
                if post == '0':
                    move_lines = self.env['account.move.line'].search(
                        [('date', '>=', start_date), ('date', '<=', end_date),
                         ('account_id', '=', chart.id), ('move_id.state', '=', 'posted')], order='id')
                else:
                    move_lines = self.env['account.move.line'].search(
                        [('date', '>=', start_date), ('date', '<=', end_date),
                         ('account_id', '=', chart.id)], order='id')
                for line in move_lines:
                    debit += line.debit
                    credit += line.credit
                    close_bal = open_bal + debit - credit
                main.append({
                    'account': chart.code + ' ' + chart.name,
                    'open_bal': open_bal,
                    'narration': False,
                    'receipt': debit,
                    'payment': credit,
                    'close_bal': close_bal,
                })

        report = self.env['ir.actions.report']._get_report_from_name(
            'accounting_reports_baykee.cash_bank_summary_temp')
        docargs = {
            'doc_ids': [],
            'doc_model': 'account.move',
            'data': data,
            'fold': fold,
            'start_date': start_date,
            'end_date': end_date,
            'main': main,
            'docs': docs,
            'company_id': company_id or False,
        }
        return docargs
