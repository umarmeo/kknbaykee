# -*- coding: utf-8 -*-

from odoo import models, fields, api


class update_purchase_module_baykee(models.Model):
    _inherit = 'purchase.order'
    _description = 'update_purchase_order'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')

    def action_temp(self):
        if len(self.order_line) >= 0:
            duplicate_list = [self.account_analytic_id, self.analytic_tag_ids]
            return duplicate_list

class update_purchase_module_baykee(models.Model):
    _inherit = 'purchase.order.line'

    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')

    @api.onchange('account_analytic_id', 'analytic_tag_ids', 'name')
    def _onchange_receive(self):
        list_receive = self.order_id.action_temp()
        self.account_analytic_id = list_receive[0]
        self.analytic_tag_ids = list_receive[1]
