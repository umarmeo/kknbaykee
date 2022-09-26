# -*- coding: utf-8 -*-

from odoo import models, fields, api


class update_employee_module_baykee(models.Model):
    _inherit = 'hr.employee'

    emp_address = fields.Char(string='Home Address')