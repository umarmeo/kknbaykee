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
    # product_ids = fields.Many2many('product.product', default=_get_product_ids)
    product_tmpl_ids = fields.Many2many('product.template', default=_get_product_tmpl_ids)

    # def _product_variant_domain(self):
    #     list_variant = []
    #     variants = self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_ids.id)])
    #     for variant in variants:
    #         list_variant.append(variant.id)
    #     return [('id', 'in', list_variant)]
    #
    # @api.model
    # def default_get(self, fields):
    #     active_model = self.env.context.get('active_model')
    #     if active_model == 'product.template' and len(self.env.context.get('active_ids', [])) <= 1:
    #         lead = self.env[active_model].browse(self.env.context.get('active_id')).exists()
    #     return rec

    product_variant = fields.Many2many('product.product', string="Product Variant")
