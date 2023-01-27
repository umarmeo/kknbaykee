from odoo import fields, models, api


class ProductMoveReportWizard(models.TransientModel):
    _name = 'product.move.wiz'
    _description = 'Product Move Report Wizard'

    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', default=fields.Date.context_today)
    product_id = fields.Many2many('product.product', string='Product')