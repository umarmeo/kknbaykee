import time
import math
import datetime
from datetime import datetime
import calendar
import logging
import calendar
from odoo.exceptions import UserError
import pdb
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)
import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class CashAndBankSummary(models.TransientModel):
    _name = 'cash.bank.summary.report'
    _description = "Cash and Bank Summary Report"

    start_date = fields.Date(string="Start Date", required=True, default=datetime.today().replace(day=1))

    @api.model
    def _default_end_date(self):
        first = datetime.today().replace(day=1)
        last = first + relativedelta(months=1) + timedelta(days=-1)
        return last

    end_date = fields.Date(string="End Date", required=True,
                           default=_default_end_date)
    fold = fields.Selection([
        ('0', 'Yes'),
        ('1', 'No')], string="Fold", required=True, default='0')

    def export_cash_and_bank_summary(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'cash.bank.summary.report',
            'form': data
        }
        return self.env.ref('accounting_reports_baykee.action_cash_bank_summary_report_template').with_context(
            landscape=False).report_action(self, data=datas, config=False)

    def export_excel(self):
        self.ensure_one()
        [data] = self.read()
        # company_id = self.env.user.company_id
        start_date = self.start_date
        end_date = self.end_date
        fold = self.fold
        main = []
        account_type = self.env['account.account.type'].search([('name', '=', 'Bank and Cash')])
        chart_of_account = self.env['account.account'].search([('user_type_id.name', '=', account_type.name)])
        for chart in chart_of_account:
            open_balance = self.env['account.move.line'].search(
                [('date', '<', start_date), ('account_id', '=', chart.id), ('move_id.state', '=', 'posted')])
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
                move_lines = self.env['account.move.line'].search(
                    [('date', '>=', start_date), ('date', '<=', end_date),
                     ('account_id', '=', chart.id), ('move_id.state', '=', 'posted')], order='id')
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
                move_lines = self.env['account.move.line'].search(
                    [('date', '>=', start_date), ('date', '<=', end_date),
                     ('account_id', '=', chart.id), ('move_id.state', '=', 'posted')], order='id')
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
        print(main)
        datas = {
            'ids': [],
            'model': 'cash.bank.summary.report',
            'form': data,
            'main': main,
        }
        return self.env.ref('accounting_reports_baykee.action_cash_bank_summary_report_xlsx').with_context(
            landscape=False).report_action(self, data=datas, config=False)
