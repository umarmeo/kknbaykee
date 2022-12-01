from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pytz
from zk import ZK, const


class ZkMachine(models.Model):
    _name = 'zk.machine.attendance'
    _inherit = 'hr.attendance'

    device_id = fields.Char(string='Biometric Device ID')
    punching_day = fields.Date(string='Date')
    attendance_type = fields.Selection([('1', 'Finger'),
                                        ('15', 'Face'),
                                        ('2', 'Card'),
                                        ('3', 'Password'),
                                        ('0', 'Password'),
                                        ('4', 'Card')], string='Category')
    punching_time = fields.Datetime(string='Punching Time')
    address_id = fields.Many2one('res.partner', string='Working Address')
    location_device = fields.Char(string='Location')


class ReportZkDevice(models.Model):
    _name = 'zk.report.daily.attendance'
    _auto = False
    _order = 'punching_day desc'

    name = fields.Many2one('hr.employee', string='Employee')
    punching_day = fields.Date(string='Date')
    address_id = fields.Many2one('res.partner', string='Working Address')
    attendance_type = fields.Selection([('1', 'Finger'),
                                        ('15', 'Face'),
                                        ('2', 'Card'),
                                        ('3', 'Password'),
                                        ('0', 'Password'),
                                        ('4', 'Card')],
                                       string='Category')
    punching_time = fields.Datetime(string='Punching Time')
    location_device = fields.Char(string='Location')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'zk_report_daily_attendance')
        self._cr.execute("""
            create or replace view zk_report_daily_attendance as (
                select
                    min(z.id) as id,
                    z.employee_id as name,
                    z.punching_day as punching_day,
                    z.address_id as address_id,
                    z.attendance_type as attendance_type,
                    z.punching_time as punching_time,
                    z.location_device as location_device
                from zk_machine_attendance z
                    join hr_employee e on (z.employee_id=e.id)
                GROUP BY
                    z.employee_id,
                    z.punching_day,
                    z.address_id,
                    z.attendance_type,
                    z.punching_time,
                    z.location_device
            )
        """)
