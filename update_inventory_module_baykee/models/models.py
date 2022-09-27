# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    extra_html = fields.Html('Extra Content', default='"Warranty Void, If Sticker Removed"')
    print_format = fields.Selection([
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('4x12xprice', '4 x 12 with price')], string="Format", default='4x12', required=True)

    class ProductTemplate(models.Model):
        _inherit = 'product.template'

        min_sale_price = fields.Float(string="Minimum Sale Price")

    class ProductProduct(models.Model):
        _inherit = 'product.product'

        min_sale_price = fields.Float(string="Minimum Sale Price")

