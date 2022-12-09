from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    month = fields.Integer(string="Month", compute='compute_month_year')
    year = fields.Integer(string="Year", compute='compute_month_year')

    @api.depends('date_from')
    def compute_month_year(self):
        for rec in self:
            if rec.date_from:
                rec.year = rec.date_from.year
                rec.month = rec.date_from.month