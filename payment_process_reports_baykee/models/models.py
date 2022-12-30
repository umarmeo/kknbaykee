from odoo import models, fields, api, _


class PaymentProcess(models.Model):
    _inherit = 'payment.process'

    month = fields.Integer(string="Month", compute='compute_month_year')
    year = fields.Integer(string="Year", compute='compute_month_year')

    @api.depends('create_date')
    def compute_month_year(self):
        for rec in self:
            if rec.create_date:
                rec.year = rec.create_date.year
                rec.month = rec.create_date.month
