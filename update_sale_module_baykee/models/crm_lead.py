# -*- coding: utf-8 -*-

from odoo import models, fields


class update_crm_lead(models.Model):
    _inherit = 'crm.lead'
    _description = 'Add two fields in CRM Analytic Account and Account Analytic Tags'

    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    def action_new_quotation(self):
        action = super().action_new_quotation()
        action['context']['default_analytic_account_id'] = self.account_analytic_id.id
        action['context']['default_analytic_tag_ids'] = self.analytic_tag_ids.id
        return action