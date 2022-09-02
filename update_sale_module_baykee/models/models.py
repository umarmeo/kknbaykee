# -*- coding: utf-8 -*-

from odoo import models, fields, api


class update_sale_module_baykee(models.Model):
    _inherit = 'sale.order'

    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale'
        }

    def action_temp(self):
        if len(self.order_line) >= 0:
            duplicate_list = [self.analytic_account_id, self.analytic_tag_ids]
            return duplicate_list

class update_sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')

    @api.onchange('account_analytic_id', 'analytic_tag_ids', 'name', 'date_order')
    def _onchange_receive(self):
        list_receive = self.order_id.action_temp()
        self.account_analytic_id = list_receive[0]
        self.analytic_tag_ids = list_receive[1]

