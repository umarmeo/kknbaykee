from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    machine_id = fields.Char(string='Machine ID')
    employee_shift = fields.Many2one('baykee.employee.shift', string='Employee Shift')
    rest_days = fields.Many2many('days.week', string='Rest Days')

    @api.constrains('machine_id')
    def check_unique_machine_id(self):
        records = self.env['hr.employee'].search(
            [('machine_id', '=', self.machine_id), ('machine_id', '!=', False), ('id', '!=', self.id)])
        if records:
            raise UserError(_('Another User with same Biometric Machine ID already exists.'))


class DaysOfWeek(models.Model):
    _name = 'days.week'

    name = fields.Char('Name')

