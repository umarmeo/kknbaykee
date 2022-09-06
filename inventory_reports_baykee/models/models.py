# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class StockQuant(models.Model):
    _inherit = 'stock.move.line'

    new_date = fields.Date('New Date', compute='_compute_date', store=True)

    @api.depends('date')
    def _compute_date(self):
        for rec in self:
            if rec.date:
                date = datetime.strptime(str(rec.date), '%Y-%m-%d %H:%M:%S').date()
                rec.new_date = date
