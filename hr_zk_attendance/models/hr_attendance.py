from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from datetime import date
import pytz
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class attendance_report_form(models.Model):
    _inherit = 'hr.attendance'

    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  tracking=True, ondelete='cascade', index=True)

    employee_code = fields.Char(related='employee_id.machine_id', string='Employee Code', tracking=True, store=True)
    shift = fields.Selection([
        ('1', '09:00 am to 06:00 pm (5 Days)'),
        ('2', '09:00 am to 05:00 pm (5 Days)'),
        ('3', '08:00 am to 04:00 pm (6 Days)'),
        ('4', '04:00 pm to 12:00 am (6 Days)'),
        ('5', '12:00 am to 08:00 am (6 Days)'),
        ('6', '09:00 am to 06:00 pm (6 Days)'),
        ('7', '05:00 pm to 02:00 am (6 Days)'),
        ('8', '03:00 pm to 12:00 am (6 Days)'),
        ('9', '12:00 am to 09:00 am (6 Days)'),
        ('10', '08:00 am to 05:00 pm (6 Days)'),
        ('11', '04:00 pm to 01:00 am (6 Days)'),
        ('12', '08:00 pm to 04:00 am (6 Days)'),
        ('13', '09:00 am to 09:00 pm'),
        ('14', '09:00 pm to 09:00 am'),
    ], string='Old Shift Time', tracking=True, readonly=True)
    new_shift = fields.Many2one('baykee.employee.shift', string='New Shift Time', tracking=True, readonly=True)
    status = fields.Selection(selection=[('PresentOnTime', 'Present'),
                                         ('Late', 'Late'),
                                         ('ShortLeave', 'Short Leave'),
                                         ('HalfLeave', 'Half Leave'),
                                         ('RestDay', 'Rest Day'),
                                         ('PaidLeave', 'Paid Leave'),
                                         ('UnpaidLeave', 'Unpaid Leave'),
                                         ('CasualLeave', 'Casual Leave'),
                                         ('SickLeave', 'Sick Leave'),
                                         ('CompensatoryLeave', 'Compensatory Leave'),
                                         ('GazetteLeave', 'Gazette Leave'),
                                         ('OfficialLeaves', 'Official Leave'),
                                         ('WorkfromHome', 'Work from Home'),
                                         ('OutdoorDuty', 'Outdoor Duty'),
                                         ('Absent', 'Absent'), ],
                              string='Check In Status', tracking=True, store=True, readonly=False)
    out_status = fields.Selection(selection=[('PresentOnTime', 'Present'),
                                             ('Late', 'Late'),
                                             ('ShortLeave', 'Short Leave'),
                                             ('HalfLeave', 'Half Leave'),
                                             ('RestDay', 'Rest Day'),
                                             ('PaidLeave', 'Paid Leave'),
                                             ('UnpaidLeave', 'Unpaid Leave'),
                                             ('CasualLeave', 'Casual Leave'),
                                             ('SickLeave', 'Sick Leave'),
                                             ('CompensatoryLeave', 'Compensatory Leave'),
                                             ('GazetteLeave', 'Gazette Leave'),
                                             ('OfficialLeaves', 'Official Leave'),
                                             ('WorkfromHome', 'Work from Home'),
                                             ('OutdoorDuty', 'Outdoor Duty'),
                                             ('Absent', 'Absent'), ],
                                  string='Check Out Status', tracking=True, store=True, readonly=False)
    is_absent = fields.Boolean('Is Absent')
    late_time = fields.Char(string='Late Check In', tracking=True, readonly=False)
    out_late_time = fields.Char(string='Early Check Out', tracking=True, readonly=False)

    late_count = fields.Char(string='Late Counts', tracking=True, readonly=True)
    leave_count = fields.Char(string='Leave Counts', tracking=True, readonly=True)
    current_shiftatt_date = fields.Date('Date', tracking=True)

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False, tracking=True)
    check_out = fields.Datetime(string="Check Out", tracking=True)

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    @api.onchange('current_shiftatt_date')
    def _onchange_current_shiftatt_date(self):
        self.status = False
        self.out_status = False
        self.late_count = False
        self.late_time = False
        self.end_date = False
        self.out_late_time = False
        self.leave_count = False
        self.check_in = False
        self.check_out = False
        self.worked_hours = 0

    @api.onchange('end_date', 'current_shiftatt_date')
    def _onchange_end_date_check(self):
        if self.end_date and self.current_shiftatt_date:
            if self.current_shiftatt_date > self.end_date:
                raise ValidationError('End Date must be greater than start date!')

    @api.onchange('check_in', 'check_out', 'employee_id', 'current_shiftatt_date')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        name = self.employee_id
        # self.shift = name.employee_shift
        self.new_shift = name.employee_shift

        if self.employee_id:
            if self.check_in and self.current_shiftatt_date:
                temp_time = datetime.strptime(str(self.check_in), '%Y-%m-%d %H:%M:%S').astimezone(
                    pytz.timezone('Asia/Karachi'))
                temp_time = datetime.strptime(str(temp_time), '%Y-%m-%d %H:%M:%S+05:00')
                shift_check = name.employee_shift
                date_check = temp_time.date()
                temp_time = datetime.strptime(str(temp_time), '%Y-%m-%d %H:%M:%S')
                shift_start = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.shift_start)
                margin_shift_start = shift_start - timedelta(hours=3)

                present_end = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.present_end)
                late_end = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.late_end)
                short_end = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.short_leave)
                if margin_shift_start <= temp_time < present_end:
                    self.late_time = False
                    self.status = 'PresentOnTime'
                elif present_end <= temp_time < late_end:
                    self.late_time = str(temp_time - shift_start)
                    self.status = 'Late'
                elif late_end <= temp_time < short_end:
                    self.late_time = str(temp_time - shift_start)
                    self.status = 'ShortLeave'
                else:
                    self.late_time = str(temp_time - shift_start)
                    if self.status == 'HalfLeave':
                        self.status = 'HalfLeave'
                    else:
                        self.status = 'Absent'

                shift_close = shift_start + timedelta(hours=shift_check.shift_duration)
                shift_late_departure_margin = shift_close - timedelta(hours=shift_check.margin)
                shift_late_departure = shift_close - timedelta(hours=1)
                shift_short_departure = shift_close - timedelta(hours=2)
                temp_time = datetime.strptime(str(self.check_out), '%Y-%m-%d %H:%M:%S').astimezone(
                    pytz.timezone('Asia/Karachi'))
                temp_time = datetime.strptime(str(temp_time), '%Y-%m-%d %H:%M:%S+05:00')

                if shift_late_departure_margin <= temp_time:
                    self.out_late_time = False
                    self.out_status = 'PresentOnTime'
                elif shift_late_departure_margin > temp_time >= shift_late_departure:
                    self.out_late_time = str(shift_close - temp_time)
                    self.out_status = 'Late'
                elif shift_late_departure > temp_time >= shift_short_departure:
                    self.out_late_time = str(shift_close - temp_time)
                    self.out_status = 'ShortLeave'
                else:
                    self.out_late_time = str(shift_close - temp_time)
                    if self.out_status == 'HalfLeave':
                        self.out_status = 'HalfLeave'
                    else:
                        self.out_status = 'Absent'

    @api.onchange('employee_id')
    def _onchange_employee_id_new(self):
        self.shift = False
        self.new_shift = False
        self.status = False
        self.late_count = False
        self.end_date = False
        self.late_time = False
        self.leave_count = False
        self.current_shiftatt_date = False
        self.check_in = False
        self.check_out = False
        self.worked_hours = 0
        if self.employee_id:
            self.new_shift = self.employee_id.new_shift_type



