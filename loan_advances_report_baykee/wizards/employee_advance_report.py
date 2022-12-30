from odoo import models, fields, api, _
from datetime import datetime


class AdvanceAgainstSalary(models.TransientModel):
    _name = 'advance.against.salary.wizard'

    month = fields.Selection([
        ('1', "January"),
        ('2', "February"),
        ('3', "March"),
        ('4', "April"),
        ('5', "May"),
        ('6', "June"),
        ('7', "July"),
        ('8', "August"),
        ('9', "September"),
        ('10', "October"),
        ('11', "November"),
        ('12', "December"),
    ], string="Month")

    @api.model
    def year_selection(self):
        year = 2018
        year_list = []
        while year != 2090:
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    year = fields.Selection(year_selection, string="Year", default=datetime.now().year)
    department_id = fields.Many2one('hr.department', string="Division")