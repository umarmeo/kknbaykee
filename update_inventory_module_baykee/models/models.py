# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class update_inventory_module_baykee(models.Model):
#     _name = 'update_inventory_module_baykee.update_inventory_module_baykee'
#     _description = 'update_inventory_module_baykee.update_inventory_module_baykee'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_sale_price = fields.Float(string="Minimum Sale Price")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    min_sale_price = fields.Float(string="Minimum Sale Price")

