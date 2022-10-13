from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductLabel(models.TransientModel):
    _name = 'product.label.baykee'

    # @api.model
    # def _get_product_ids(self):
    #     if self.env.context.get('active_model', False) == 'product.product' and self.env.context.get(
    #             'active_ids', False):
    #         return self.env.context['active_ids']

    @api.model
    def _get_product_tmpl_ids(self):
        if self.env.context.get('active_model', False) == 'product.template' and self.env.context.get(
                'active_ids', False):
            return self.env.context['active_ids']

    quantity = fields.Integer(string="Quantity", default=1)
    extra_content = fields.Char(string="Extra Content", default='"Warranty Void, If Sticker Removed"')
    is_lot_serial = fields.Selection([
        ('0', "No"),
        ('1', "Yes"),
    ], string="Lot/Serial", default="0")
    product_tmpl_ids = fields.Many2many('product.template', default=_get_product_tmpl_ids)
    check_variant = fields.Boolean(string="Check Variant", default=False)
    variant_specific = fields.Selection([
        ('0', "No"),
        ('1', "Yes"),
    ], string="Lot Specific", default="0")
    lot_serial_no = fields.Many2many('stock.production.lot', string="Lot/Serial Number")


    @api.model
    def default_get(self, fields):
        res = super(ProductLabel, self).default_get(fields)
        res_id = self.env.context.get('active_id')
        variants = self.env['product.product'].search([('product_tmpl_id', '=', res_id), ('product_template_variant_value_ids', '!=', False)])
        res['product_variant'] = variants.ids
        res['product_variant_dummy'] = variants.ids
        if variants:
            res['check_variant'] = True
        return res

    product_variant = fields.Many2many('product.product', string="Product Variant")
    product_variant_dummy = fields.Many2many('product.product', 'dummy', string="Product Variant")

    @api.onchange('product_variant_dummy')
    def onchange_product_tmpl_ids(self):
        return {'domain': {'product_variant': [('id', '=', self.product_variant_dummy.ids)]}}

    @api.onchange('variant_specific', 'lot_serial_no')
    def onchange_variant_specific(self):
        lots = []
        res_id = self._context.get('active_id')
        products = self.env['product.product'].search([('product_tmpl_id', '=', res_id)])
        for product in products:
            lot_serial_no = self.env['stock.production.lot'].search([('product_id', '=', product.id)])
            for lot in lot_serial_no:
                lots.append(lot.id)
        return {'domain': {'lot_serial_no': [('id', 'in', lots)]}}
