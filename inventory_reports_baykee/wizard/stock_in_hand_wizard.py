from odoo import fields, models, api


class StockInHandWizard(models.TransientModel):
    _name = 'stock.in.hand.wizard'

    product_ids = fields.Many2many('product.product', string="Products")
    location_id = fields.Many2one('stock.location', 'Locations')
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 default=lambda self: self.env.company)
    date = fields.Date('Date', required=True)
