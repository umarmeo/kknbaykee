from odoo import fields, models, api, _


class SlowMoveWiz(models.TransientModel):
    _name = 'slow.move.wiz'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    location_id = fields.Many2many('stock.location', string="Location", required=True)