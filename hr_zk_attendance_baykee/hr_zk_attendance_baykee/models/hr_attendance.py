from odoo import models, fields, api
from datetime import datetime, date
from datetime import timedelta
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
                                         ('MarriageLeave', 'Marriage Leave'),
                                         ('BloodRelationDeathLeave', 'Blood Relation Death Leave'),
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
                                             ('MarriageLeave', 'Marriage Leave'),
                                             ('BloodRelationDeathLeave', 'Blood Relation Death Leave'),
                                             ('CasualLeave', 'Casual Leave'),
                                             ('SickLeave', 'Sick Leave'),
                                             ('CompensatoryLeave', 'Compensatory Leave'),
                                             ('GazetteLeave', 'Gazette Leave'),
                                             ('OfficialLeaves', 'Official Leave'),
                                             ('WorkfromHome', 'Work from Home'),
                                             ('OutdoorDuty', 'Outdoor Duty'),
                                             ('Absent', 'Absent'), ],
                                  string='Check Out Status', tracking=True, store=True, readonly=False)
    status_leave = fields.Selection(selection=[('PresentOnTime', 'Present'),
                                               ('Late', 'Late'),
                                               ('ShortLeave(unpaid)', 'Short Leave Unpaid'),
                                               ('ShortLeave(paid)', 'Short Leave Paid'),
                                               ('HalfLeave(unpaid)', 'Half Leave Unpaid'),
                                               ('HalfLeave(paid)', 'Half Leave Paid'),
                                               ('RestDay', 'Rest Day'),
                                               ('PaidLeave', 'Paid Leave'),
                                               ('UnpaidLeave', 'Unpaid Leave'),
                                               ('MarriageLeave', 'Marriage Leave'),
                                               ('BloodRelationDeathLeave', 'Blood Relation Death Leave'),
                                               ('CasualLeave', 'Casual Leave'),
                                               ('SickLeave', 'Sick Leave'),
                                               ('CompensatoryLeave', 'Compensatory Leave'),
                                               ('GazetteLeave', 'Gazette Leave'),
                                               ('OfficialLeaves', 'Official Leave'),
                                               ('WorkfromHome', 'Work from Home'),
                                               ('Absent', 'Absent'), ],
                                    string='Leave Status', tracking=False, store=True, readonly=False)
    is_absent = fields.Boolean('Is Absent')
    late_time = fields.Char(string='Late Check In', tracking=True, readonly=False)
    out_late_time = fields.Char(string='Early Check Out', tracking=True, readonly=False)

    late_count = fields.Char(string='Late Counts', tracking=True, readonly=True)
    leave_count = fields.Char(string='Leave Counts', tracking=True, readonly=True)
    current_shiftatt_date = fields.Date('Date', tracking=True)

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False, tracking=True)
    check_out = fields.Datetime(string="Check Out", tracking=True)
    timeoff_id1 = fields.Many2one('hr.leave', string='TimeOff Ref 2nd')
    timeoff_id = fields.Many2one('hr.leave', string='TimeOff Ref')

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
        self.out_late_time = False
        self.leave_count = False
        self.check_in = False
        self.check_out = False
        self.worked_hours = 0

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
                shift_start = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.shift_start)
                margin_shift_start = shift_start - timedelta(hours=3)
                present_end = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.present_end)
                late_end = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.late_end)
                short_end = datetime(date_check.year, date_check.month, date_check.day) + timedelta(
                    hours=shift_check.short_leave)
                half_end = datetime(date_check.year, date_check.month,
                                    date_check.day) + timedelta(
                    hours=shift_check.half_leave)
                if margin_shift_start <= temp_time < present_end:
                    self.late_time = False
                    self.status = 'PresentOnTime'
                elif present_end <= temp_time < late_end:
                    self.late_time = str(temp_time - present_end)
                    self.status = 'Late'
                elif late_end <= temp_time < short_end:
                    self.late_time = str(temp_time - present_end)
                    self.status = 'ShortLeave'
                elif late_end <= temp_time < half_end:
                    self.late_time = str(temp_time - present_end)
                    self.status = 'HalfLeave'
                else:
                    self.status = 'Absent'
            if self.check_out and self.current_shiftatt_date:
                shift_close = shift_start + timedelta(hours=shift_check.shift_duration)
                shift_late_departure_margin = shift_close - timedelta(hours=shift_check.margin)
                shift_late_departure = shift_close - timedelta(hours=1)
                shift_short_departure = shift_close - timedelta(hours=2)
                shift_half_departure = shift_close - timedelta(hours=4)
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
                elif shift_late_departure > temp_time >= shift_half_departure:
                    self.out_late_time = str(shift_close - temp_time)
                    self.out_status = 'HalfLeave'
                else:
                    self.out_status = 'Absent'

    @api.onchange('employee_id')
    def _onchange_employee_id_new(self):
        self.shift = False
        self.new_shift = False
        self.status = False
        self.late_count = False
        self.late_time = False
        self.leave_count = False
        self.current_shiftatt_date = False
        self.check_in = False
        self.check_out = False
        self.worked_hours = 0
        if self.employee_id:
            self.new_shift = self.employee_id.employee_shift

    def cron_download(self):
        self.add_absent_leave(start_work=True)

    def add_absent_leave(self, start_work=False):
        weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
        if start_work:
            delete_date = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                           26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
            for i in delete_date:
                date_check = date.today() - timedelta(days=i)
                date_hour_start = str(date(date_check.year, 3, 13))
                date_hour_end = str(date(date_check.year, 11, 7))
                attendance = self.env['hr.attendance'].search([('current_shiftatt_date', '=', date_check)])
                if len(attendance) > 0:
                    id = []
                    for emp in attendance:
                        id.append(emp.employee_id.id)
                    employees = self.env['hr.employee'].search([('id', 'not in', id)])
                else:
                    employees = self.env['hr.employee'].search([])
                for employee in employees:
                    if employee.name != 'System':
                        rest_day = []
                        for rest in employee.rest_days:
                            rest_day.append(weekDays[int(rest.id) - 1])
                        if date_check.strftime("%A") in rest_day:
                            status = 'RestDay'
                        else:
                            status = 'Absent'
                        start_date = date_check
                        if employee.employee_shift:
                            check_in = datetime(start_date.year, start_date.month,
                                                start_date.day) + timedelta(
                                hours=employee.employee_shift.shift_start)
                            now_dubai = check_in.astimezone(pytz.timezone('Canada/Eastern'))
                            if employee.employee_shift.shift_type == 'Night':
                                now_dubai += timedelta(days=1)
                            atten_time1 = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                            if date_hour_start < str(atten_time1).split()[0] < date_hour_end:
                                check_in = now_dubai - timedelta(hours=1)
                                check_in = check_in.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                check_in = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            check_in = False
                        att_vals = {
                            'employee_id': employee.id,
                            'current_shiftatt_date': start_date,
                            'check_in': check_in,
                            'check_out': check_in,
                            'new_shift': employee.employee_shift.id if employee.employee_shift else False,
                            'status': status,
                            'is_absent': True,
                            'out_status': status,
                            'late_time': False,
                        }
                        check_record = self.env['hr.attendance'].search(
                            [('employee_id', '=', employee.id), ('current_shiftatt_date', '=', start_date)])
                        if len(check_record) == 1:
                            pass
                        else:
                            self.env['hr.attendance'].create(att_vals)
