# -*- coding: utf-8 -*-

from odoo import models, fields, api


class update_account_move_baykee(models.Model):
    _inherit = 'account.move'

    # sale_id = fields.Many2one('sale.order', string="Sale order")
    # def button_post(self):
    #     super(update_account_move_baykee, self).button_post()
    #     for rec in self:
    #         for line in rec.line_ids:
    #             if line.account_type == 'custody' and line.selected == True:
    #                 custody = line.custody_settlement_id
    #                 move_vals = {
    #                     'name': line.payment_ref,
    #                     'date': line.date,
    #                     'partner_id': line.partner_id.id,
    #                     'ref': line.custody_settlement_id.name,
    #                     'journal_id': rec.journal_id.id,
    #                     'analytic_account_id': line.sale_id.analytic_account_id,
    #                 }
    #                 move_id = custody.env['account.move'].create(move_vals)
    #                 custody.update({'line_ids': move_id})

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # OVERRIDE
    #     ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
    #     BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')
    #
    #     for vals in vals_list:
    #         move = self.env['account.move'].browse(vals['move_id'])
    #         vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message
    #
    #         # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
    #         # company.
    #         currency_id = vals.get('currency_id') or move.company_id.currency_id.id
    #         if currency_id == move.company_id.currency_id.id:
    #             balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
    #             vals.update({
    #                 'currency_id': currency_id,
    #                 'amount_currency': balance,
    #             })
    #         else:
    #             vals['amount_currency'] = vals.get('amount_currency', 0.0)
    #
    #         if move.is_invoice(include_receipts=True):
    #             currency = move.currency_id
    #             partner = self.env['res.partner'].browse(vals.get('partner_id'))
    #             taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
    #             tax_ids = set(taxes.ids)
    #             taxes = self.env['account.tax'].browse(tax_ids)
    #             analytic_account_id = self.env['sale.order'].browse(vals.get('analytic_account_id'))
    #
    #             # Ensure consistency between accounting & business fields.
    #             # As we can't express such synchronization as computed fields without cycling, we need to do it both
    #             # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
    #             # business [resp. accounting] fields are recomputed.
    #             if any(vals.get(field) for field in ACCOUNTING_FIELDS):
    #                 price_subtotal = self._get_price_total_and_subtotal_model(
    #                     vals.get('price_unit', 0.0),
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     currency,
    #                     self.env['product.product'].browse(vals.get('product_id')),
    #                     self.env['sale.order'].browse(vals.get('analytic_account_id')),
    #                     partner,
    #                     taxes,
    #                     move.move_type,
    #                 ).get('price_subtotal', 0.0)
    #                 vals.update(self._get_fields_onchange_balance_model(
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('analytic_account_id'),
    #                     vals['amount_currency'],
    #                     move.move_type,
    #                     currency,
    #                     taxes,
    #                     price_subtotal
    #                 ))
    #                 vals.update(self._get_price_total_and_subtotal_model(
    #                     vals.get('price_unit', 0.0),
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('analytic_account_id'),
    #                     currency,
    #                     self.env['product.product'].browse(vals.get('product_id')),
    #                     self.env['sale.order'].browse(vals.get('analytic_account_id')),
    #                     partner,
    #                     taxes,
    #                     move.move_type,
    #                 ))
    #             elif any(vals.get(field) for field in BUSINESS_FIELDS):
    #                 vals.update(self._get_price_total_and_subtotal_model(
    #                     vals.get('price_unit', 0.0),
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('analytic_account_id'),
    #                     vals['amount_currency'],
    #                     currency,
    #                     self.env['product.product'].browse(vals.get('product_id')),
    #                     partner,
    #                     taxes,
    #                     move.move_type,
    #                     self.env['sale.order'].browse(analytic_account_id),
    #                 ))
    #                 vals.update(self._get_fields_onchange_subtotal_model(
    #                     vals['price_subtotal'],
    #                     move.move_type,
    #                     currency,
    #                     move.company_id,
    #                     move.date,
    #                     analytic_account_id,
    #                     vals.get('analytic_account_id'),
    #                 ))
    #
    #     lines = super(update_account_move_baykee, self).create(vals_list)
    #
    #     moves = lines.mapped('move_id')
    #     if self._context.get('check_move_validity', True):
    #         moves._check_balanced()
    #     moves.filtered(lambda m: m.state == 'posted')._check_fiscalyear_lock_date()
    #     lines.filtered(lambda l: l.parent_state == 'posted')._check_tax_lock_date()
    #     moves._synchronize_business_models({'line_ids'})
    #
    #     return lines


# sale_id = fields.Many2one('sale.order')
    # def _prepare_invoice_line(self):
    #     res = super(update_account_move_baykee, self)._prepare_invoice_line()
    #     res.update({'analytic_account_id': self.sale_id.analytic_account_id,
    #                 'analytic_tag_ids': self.sale_id.analytic_tag_ids})
    #     return res