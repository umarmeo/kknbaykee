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


class PartnerLedgerReport(models.TransientModel):
    _name = 'partner.ledger.report'
    _description = "Partner Ledger Report"

    partner_id = fields.Many2many('res.partner', string="Partner")
    analytical_account_id = fields.Many2many('account.analytic.account', string="Analytical Account")
    analytical_tag_id = fields.Many2many('account.analytic.tag', string="Analytical Tags")
    start_date = fields.Date(string="Start Date", required=True, default=datetime.today().replace(day=1))

    @api.model
    def _default_end_date(self):
        first = datetime.today().replace(day=1)
        last = first + relativedelta(months=1) + timedelta(days=-1)
        return last

    end_date = fields.Date(string="End Date", required=True,
                           default=_default_end_date)

    def export_excel(self):
        self.ensure_one()
        [data] = self.read()
        start_date = self.start_date
        end_date = self.end_date
        partners = self.partner_id
        analytic_accounts = self.analytical_account_id
        analytic_tags = self.analytical_tag_id
        main = []
        partner_domain = []
        analytic_account_domain = []
        analytic_tag_domain = []
        partner_list = []
        analytic_account_list = []
        analytic_tag_list = []
        for p in partners:
            partner_list.append(p.id)
        if partner_list:
            partner_domain += [('id', 'in', partner_list)]
        for aa in analytic_accounts:
            analytic_account_list.append(aa.id)
        if analytic_account_list:
            analytic_account_domain += [('id', 'in', analytic_account_list)]
        for at in analytic_tags:
            analytic_tag_list.append(at.id)
        if analytic_tag_list:
            analytic_tag_domain += [('id', 'in', analytic_tag_list)]
        partner_search = self.env['res.partner'].search(partner_domain)
        for part in partner_search:
            open_balance = self.env['account.move.line'].search(
                [('date', '<', start_date), ('partner_id', '=', part.id),
                 ('move_id.state', '=', 'posted')])
            open_bal = 0
            for op in open_balance:
                open_bal += op.balance
            main.append({
                'partner': part.name,
                'analytic_account': False,
                'analytic_tag': False,
                'account': False,
                'open_bal': open_bal,
                'narration': False,
                'receipt': False,
                'payment': False,
                'close_bal': open_bal,
            })
            analytic_account_search = self.env['account.analytic.account'].search(analytic_account_domain)
            for account in analytic_account_search:
                main.append({
                    'partner': False,
                    'analytic_account': account.name,
                    'analytic_tag': False,
                    'account': False,
                    'open_bal': False,
                    'narration': False,
                    'receipt': False,
                    'payment': False,
                    'close_bal': False,
                })
                analytic_tag_search = self.env['account.analytic.tag'].search(analytic_tag_domain)
                for tag in analytic_tag_search:
                    main.append({
                        'partner': False,
                        'analytic_account': False,
                        'analytic_tag': tag.name,
                        'account': False,
                        'open_bal': False,
                        'narration': False,
                        'receipt': False,
                        'payment': False,
                        'close_bal': False,
                    })
                    move_lines = self.env['account.move.line'].search(
                        [('date', '>=', start_date), ('date', '<=', end_date),
                         ('partner_id', '=', part.id), ('analytic_tag_ids', '=', tag.id),
                         ('analytic_account_id', '=', account.id), ('move_id.state', '=', 'posted')], order='id')
                    close_bal = 0
                    for line in move_lines:
                        close_bal += line.balance
                        main.append({
                            'partner': False,
                            'analytic_account': False,
                            'analytic_tag': False,
                            'account': line.account_id.name,
                            'open_bal': False,
                            'narration': line.name,
                            'receipt': line.debit,
                            'payment': line.credit,
                            'close_bal': close_bal,
                        })
        datas = {
            'ids': [],
            'model': 'partner.ledger.report',
            'form': data,
            'main': main,
        }
        return self.env.ref('accounting_reports_baykee.action_partner_ledger_report_xlsx').with_context(
            landscape=False).report_action(self, data=datas, config=False)
