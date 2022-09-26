# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    new_date = fields.Date('New Date', compute='_compute_in_date', store=True)

    @api.depends('in_date')
    def _compute_in_date(self):
        for rec in self:
            if rec.in_date:
                date = datetime.strptime(str(rec.in_date), '%Y-%m-%d %H:%M:%S').date()
                rec.new_date = date
