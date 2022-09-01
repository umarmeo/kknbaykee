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
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        partners = docs.partner_id
        analytic_accounts = docs.analytical_account_id
        analytic_tags = docs.analytical_tag_id
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

        report = self.env['ir.actions.report']._get_report_from_name(
            'accounting_reports_baykee.partner_ledger_temp')
        docargs = {
            'doc_ids': [],
            'doc_model': 'account.move',
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'main': main,
            'docs': docs,
            'company_id': company_id or False,
        }
        return docargs
