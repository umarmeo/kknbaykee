import json
import requests
import pytz
from datetime import datetime, date
from dateutil import parser
from datetime import timedelta
import logging
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
from zk import ZK

log = logging.getLogger(__name__)


class ZkMachine(models.Model):
    _name = 'zk.machine'

    name = fields.Char(string='Machine', required=True)
    machine_ip = fields.Char("Machine IP/DNS", required=True)
    port_no = fields.Integer(string='Port No', required=True, default="4370")
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    zk_timeout = fields.Integer(string='ZK Timeout', required=True, default="120")
    zk_after_date = fields.Datetime(string='Attend Start Date',
                                    help='If provided, Attendance module will ignore records before this date.')
    machine_location = fields.Char(string="Machine Location")
    last_run_status = fields.Boolean('Machine OK', default=False)
    last_error_msg = fields.Char("Last Error")
    serial_num = fields.Char("Serial num", readonly=True)

    # def device_connect(self, zkobj):
    #     try:
    #         conn = zkobj.connect()
    #         return conn
    #     except:
    #         _logger.info("zk.exception.ZKNetworkError: can't reach device.")
    #         raise UserError("Connection To Device cannot be established.")

    def try_connection(self):
        conn, _ = self.connect()
        res = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection status',
                'message': '',
                'sticky': False,
            }
        }
        if conn:
            conn.disconnect()
            res['params']['message'] = 'SUCCESS'
            res['params']['type'] = 'success'
        else:
            res['params']['message'] = "Failed to connect: {0}".format(self.last_error_msg)
            res['params']['type'] = 'danger'

        return res

    def connect(self):
        """
        Connects and returns a connection object or exception if not connected
        @requires: pyzk module

        @return: connection object, ZK object
        """
        zk, conn = None, None
        try:
            zk = ZK(self.machine_ip, port=self.port_no, password=0, timeout=self.zk_timeout, ommit_ping=True)
            conn = zk.connect()

            self.last_run_status = True
            self.last_error_msg = None
            self.serial_num = conn.get_serialnumber()
        except Exception as ex:
            log.error("Failed to connect to: %s[%s:%s]", self.name, self.machine_ip, self.port_no, exc_info=1)
            self.last_run_status, self.last_error_msg = False, str(ex)

        return conn, zk

    def clear_attendance(self):
        pass

    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        log.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        conn = None
        total_attendance_rec, total_users = 0, 0
        try:
            conn, _ = self.connect()
            if conn:
                attendance = conn.get_attendance()
                machine_users = conn.get_users()
                total_attendance_rec, total_users = len(attendance), len(machine_users)
                if attendance:
                    weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
                    date_hour_start = str(date(date.today().year, 3, 13))
                    date_hour_end = str(date(date.today().year, 11, 7))
                    start_date_check_attendance = str(date.today() - timedelta(days=60))
                    for each in attendance:
                        timedate = datetime.strptime(each.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                                     '%Y-%m-%d %H:%M:%S')
                        if start_date_check_attendance < str(timedate).split()[0] <= str(date.today()):
                            now_dubai = timedate.astimezone(pytz.timezone('Canada/Eastern'))
                            atten_time1 = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                            if date_hour_start < str(atten_time1).split()[0] < date_hour_end:
                                atten_time = now_dubai - timedelta(hours=1)
                                atten_time = atten_time.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                atten_time = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                            timendate = str(atten_time).split()
                            name = self.env['hr.employee'].search([('machine_id', '=', each.user_id)])
                            duplicate_atten_ids = zk_attendance.search(
                                [('employee_id', '=', name.id), ('punching_time', '=', atten_time)])
                            if len(duplicate_atten_ids) > 0:
                                continue
                            else:
                                if len(name) == 1:
                                    shift_check = name.employee_shift
                                    if shift_check:
                                        temp_time = datetime.strptime(str(atten_time),
                                                                      '%Y-%m-%d %H:%M:%S').astimezone(
                                            pytz.timezone('Asia/Karachi'))
                                        temp_time = datetime.strptime(str(temp_time), '%Y-%m-%d %H:%M:%S+05:00')
                                        date_check = temp_time.date()
                                        attendance_date_check = temp_time.date()
                                        temp_time = datetime.strptime(str(temp_time), '%Y-%m-%d %H:%M:%S')
                                        shift_start = datetime(date_check.year, date_check.month,
                                                               date_check.day) + timedelta(
                                            hours=shift_check.shift_start)
                                        margin_shift_start = shift_start - timedelta(hours=3)

                                        present_end = datetime(date_check.year, date_check.month,
                                                               date_check.day) + timedelta(
                                            hours=shift_check.present_end)
                                        late_end = datetime(date_check.year, date_check.month,
                                                            date_check.day) + timedelta(
                                            hours=shift_check.late_end)
                                        short_end = datetime(date_check.year, date_check.month,
                                                             date_check.day) + timedelta(
                                            hours=shift_check.short_leave)
                                        half_end = datetime(date_check.year, date_check.month,
                                                            date_check.day) + timedelta(
                                            hours=shift_check.half_leave)
                                        shift_end = shift_start + timedelta(
                                            hours=(shift_check.shift_duration + 4))
                                        shift_close = shift_start + timedelta(hours=shift_check.shift_duration)
                                        shift_late_departure_margin = shift_close - timedelta(
                                            hours=shift_check.margin)
                                        shift_late_departure = shift_close - timedelta(hours=1)
                                        shift_short_departure = shift_close - timedelta(hours=2)

                                        check_record = self.env['hr.attendance'].search(
                                            [('employee_id', '=', name.id),
                                             ('current_shiftatt_date', '=', attendance_date_check)])
                                        if len(check_record) == 1:
                                            if check_record.is_absent:
                                                check_record.with_context(force_delete=True).unlink()
                                                check_record = self.env['hr.attendance']
                                        if len(check_record) == 0:
                                            rest_day = []
                                            for rest in name.rest_days:
                                                rest_day.append(weekDays[int(rest.id) - 1])
                                            date_check1 = temp_time.date()
                                            if date_check1.strftime("%A") in rest_day:
                                                att_vals = {
                                                    'employee_id': name.id,
                                                    'current_shiftatt_date': attendance_date_check,
                                                    'check_in': atten_time,
                                                    'check_out': atten_time,
                                                    'status': 'PresentOnTime',
                                                    'out_status': 'PresentOnTime',
                                                    'new_shift': shift_check.id,
                                                    # 'late_count': str(late_count),
                                                }
                                                self.env['hr.attendance'].create(att_vals)
                                            elif margin_shift_start <= temp_time < present_end:
                                                att_vals = {
                                                    'employee_id': name.id,
                                                    'current_shiftatt_date': attendance_date_check,
                                                    'check_in': atten_time,
                                                    'check_out': atten_time,
                                                    'status': 'PresentOnTime',
                                                    'out_status': 'Absent',
                                                    'new_shift': shift_check.id,
                                                }
                                                self.env['hr.attendance'].create(att_vals)
                                            elif present_end <= temp_time < late_end:
                                                att_vals = {
                                                    'employee_id': name.id,
                                                    'current_shiftatt_date': attendance_date_check,
                                                    'check_in': atten_time,
                                                    'check_out': atten_time,
                                                    'status': 'Late',
                                                    'new_shift': shift_check.id,
                                                    'late_time': str(temp_time - present_end),
                                                    'out_status': 'Absent',
                                                    'out_late_time': False,
                                                }
                                                self.env['hr.attendance'].create(att_vals)
                                            elif late_end <= temp_time < short_end:
                                                att_vals = {
                                                    'employee_id': name.id,
                                                    'current_shiftatt_date': attendance_date_check,
                                                    'check_in': atten_time,
                                                    'check_out': atten_time,
                                                    'new_shift': shift_check.id,
                                                    'status': 'ShortLeave',
                                                    'out_status': 'Absent',
                                                    'late_time': str(temp_time - present_end),
                                                    'out_late_time': False,
                                                }
                                                self.env['hr.attendance'].create(att_vals)
                                            elif late_end <= temp_time < half_end:
                                                att_vals = {
                                                    'employee_id': name.id,
                                                    'current_shiftatt_date': attendance_date_check,
                                                    'check_in': atten_time,
                                                    'check_out': atten_time,
                                                    'new_shift': shift_check.id,
                                                    'status': 'HalfLeave',
                                                    'out_status': 'Absent',
                                                    'late_time': str(temp_time - present_end),
                                                    'out_late_time': False,
                                                }
                                                self.env['hr.attendance'].create(att_vals)
                                            else:
                                                att_vals = {
                                                    'employee_id': name.id,
                                                    'current_shiftatt_date': attendance_date_check,
                                                    'check_in': atten_time,
                                                    'new_shift': shift_check.id,
                                                    'check_out': atten_time,
                                                    'status': 'Absent',
                                                    'out_status': 'Absent',
                                                    'late_time': False,
                                                    'out_late_time': False,
                                                }
                                                self.env['hr.attendance'].create(att_vals)
                                        elif len(check_record) == 1:
                                            temp_check_out = False
                                            temp_time1 = datetime.strptime(str(check_record.check_in),
                                                                           '%Y-%m-%d %H:%M:%S').astimezone(
                                                pytz.timezone('Asia/Karachi'))
                                            temp_time1 = datetime.strptime(str(temp_time1),
                                                                           '%Y-%m-%d %H:%M:%S+05:00')
                                            if temp_time1 > temp_time:
                                                if len(check_record.timeoff_id) == 0:
                                                    if margin_shift_start <= temp_time < present_end:
                                                        check_record.status = 'PresentOnTime'
                                                        check_record.status_leave = 'PresentOnTime'
                                                        check_record.late_time = False
                                                    elif present_end <= temp_time < late_end:
                                                        check_record.status = 'Late'
                                                        check_record.status_leave = 'Late'
                                                        check_record.late_time = str(temp_time - present_end)
                                                    elif late_end <= temp_time < short_end:
                                                        check_record.status = 'ShortLeave'
                                                        check_record.status_leave = 'ShortLeave(paid)'
                                                        check_record.late_time = str(temp_time - present_end)
                                                    elif late_end <= temp_time < half_end:
                                                        check_record.status = 'HalfLeave'
                                                        check_record.late_time = str(temp_time - present_end)
                                                temp1 = check_record.check_in
                                                check_record.check_in = atten_time
                                                check_record.check_out = temp1
                                                temp_check_out = True
                                            else:
                                                if shift_end > temp_time >= present_end:
                                                    temp_time1 = datetime.strptime(str(check_record.check_out),
                                                                                   '%Y-%m-%d %H:%M:%S').astimezone(
                                                        pytz.timezone('Asia/Karachi'))
                                                    temp_time1 = datetime.strptime(str(temp_time1),
                                                                                   '%Y-%m-%d %H:%M:%S+05:00')
                                                    if temp_time1 < temp_time:
                                                        check_record.check_out = atten_time
                                                        temp_check_out = True
                                            if temp_check_out:
                                                temp_time = datetime.strptime(str(check_record.check_out),
                                                                              '%Y-%m-%d %H:%M:%S').astimezone(
                                                    pytz.timezone('Asia/Karachi'))
                                                temp_time = datetime.strptime(str(temp_time),
                                                                              '%Y-%m-%d %H:%M:%S+05:00')
                                                if check_record.out_status not in (
                                                        'CasualLeave', 'PaidLeave', 'UnpaidLeave',
                                                        'OutdoorDuty',
                                                        'WorkfromHome', 'SickLeave', 'CompensatoryLeave',
                                                        'GazetteLeave', 'OfficialLeaves'):
                                                    rest_day = []
                                                    for rest in name.rest_days:
                                                        rest_day.append(weekDays[int(rest.id) - 1])
                                                    date_check1 = temp_time.date()
                                                    if date_check1.strftime("%A") in rest_day:
                                                        check_record.out_late_time = False
                                                        check_record.out_status = 'PresentOnTime'
                                                    elif shift_late_departure_margin <= temp_time:
                                                        check_record.out_late_time = False
                                                        check_record.out_status = 'PresentOnTime'
                                                    elif shift_late_departure_margin > temp_time >= shift_late_departure:
                                                        check_record.out_late_time = str(
                                                            shift_close - temp_time)
                                                        check_record.out_status = 'Late'
                                                    elif shift_late_departure > temp_time >= shift_short_departure:
                                                        check_record.out_late_time = str(
                                                            shift_close - temp_time)
                                                        check_record.out_status = 'ShortLeave'
                                                    else:
                                                        check_record.out_late_time = str(
                                                            shift_close - temp_time)
                                                        if check_record.out_status == 'HalfLeave':
                                                            check_record.out_status = 'HalfLeave'
                                                        else:
                                                            check_record.out_status = 'Absent'
                                    zk_attendance.create({'employee_id': name.id,
                                                          'device_id': each.user_id,
                                                          'punching_day': timendate[0],
                                                          'attendance_type': str(each.status),
                                                          'location_device': str(self.machine_ip),
                                                          'punching_time': atten_time})

            else:
                log.warn("Failed to connect to %s", self.name)
        finally:
            if conn: conn.disconnect()

        log.info(
            'Finish import machine %s -> %s attendance records for %s users.',
            self.name, total_attendance_rec, total_users)

        res = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Download status',
                'message': 'Imported %s attendance records for %s users.' % (
                    total_attendance_rec, total_users),
                'sticky': False,
                'type': 'success',
            }
        }

        return res


class BaykeeUser(models.Model):
    _name = 'baykee.user'
    _rec_name = 'user_id'
    name = fields.Char(string="name")
    user_id = fields.Char()
