from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PartnerLedgerTemplate(models.AbstractModel):
    _name = 'report.accounting_reports_baykee.partner_ledger_temp'
    _description = 'Partner Ledger Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['partner.ledger.report'].browse(docids[0])
        start_date = docs.start_date
        end_date = docs.end_date
        partners = docs.partner_id
        analytic_accounts = docs.analytical_account_id.ids if docs.analytical_account_id else []
        analytic_tags = docs.analytical_tag_id.ids if docs.analytical_tag_id else []
        data_temp = []
        temp1 = []
        deb = []
        cre = []
        credit = 0
        debit = 0
        balance = 0
        part_domain = []
        partner_list = []
        for p in partners:
            partner_list.append(p.id)
        if partner_list:
            part_domain += [('id', 'in', partner_list)]
        partner_search = self.env['res.partner'].search(part_domain)
        for partner in partner_search:
            domain = [('date', '<', start_date),
                      ('partner_id', '=', partner.id),
                      ('move_id.state', '=', 'posted')]
            if analytic_accounts:
                domain.append(('analytic_account_id', '=', analytic_accounts))
            if analytic_tags:
                domain.append(('analytic_tag_ids', '=', analytic_tags))
            data_complete = self.env['account.move.line'].search(domain)
            for line in data_complete:
                credit += line.credit
                debit += line.debit
                balance += line.balance
            vals = {
                'date': False,
                'jrnl': False,
                'account': False,
                'narration': False,
                'debit': debit,
                'credit': credit,
                'balance': balance,
            }
            temp1.append(vals)

            temp = []
            # partner1 = self.env['account.account'].search([('id', '=', partner)])
            domain = [('date', '>=', start_date), ('date', '<=', end_date),
                      ('partner_id', '=', partner.id), ('move_id.state', '=', 'posted')]
            if analytic_accounts:
                domain.append(('analytic_account_id', '=', analytic_accounts))
            if analytic_tags:
                domain.append(('analytic_tag_ids', '=', analytic_tags))
            data_complete = self.env['account.move.line'].search(domain).sorted(key=lambda r: r.date)
            for line in data_complete:
                balance += line.balance
                vals = {
                    'date': line.date,
                    'jrnl': line.journal_id.code,
                    'account': line.account_id.code,
                    'narration': line.name,
                    'debit': line.debit,
                    'credit': line.credit,
                    'balance': balance,
                }
                credit += line.credit
                debit += line.debit
                temp.append(vals)
            temp2 = temp
            data_temp.append(
                [partner.name, temp2, debit, credit, balance])
        return {
            'doc_ids': self.ids,
            'doc_model': 'account.move.line',
            'start_date': start_date,
            'end_date': end_date,
            'analytic_accounts': docs.analytical_account_id,
            'analytic_accounts_all': "All",
            'analytic_tags': docs.analytical_tag_id,
            'analytic_tags_all': "All",
            'dat': data_temp,
            'data': data,
        }