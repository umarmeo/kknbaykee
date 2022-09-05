# -*- coding: utf-8 -*-

from odoo import models, fields, api


class update_purchase_order(models.Model):
    _inherit = 'purchase.order'
    _description = 'update_purchase_order'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')

    @api.onchange('account_analytic_id', 'analytic_tag_ids')
    def _onchange_purchase_order_analytic(self):
        for line in self.order_line:
            line.account_analytic_id = self.account_analytic_id
            line.analytic_tag_ids = self.analytic_tag_ids

    def data_send(self):
        duplicate_list = [self.account_analytic_id, self.analytic_tag_ids]
        return duplicate_list

class update_purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')

    @api.onchange('account_analytic_id', 'analytic_tag_ids', 'order_id')
    def _onchange_purchase_order_line(self):
        list_receive = self.order_id.data_send()
        self.account_analytic_id = list_receive[0]
        self.analytic_tag_ids = list_receive[1]
