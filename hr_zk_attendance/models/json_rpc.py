import json
import requests
from odoo import models, fields, api, _
from dateutil import parser
import pytz
from datetime import datetime, date
from datetime import timedelta
import os
import platform
from odoo.exceptions import UserError, ValidationError
import subprocess


class Attendance(models.Model):
    _inherit = 'zk.machine'

    def check_connection_api(self):
        data = {}
        url = "http://103.115.197.23/ping?ip=%s" % self.name
        response = requests.get(url, data=json.dumps(data))
        ping = json.loads(response.text)
        if platform.system() == 'Linux':
            if ping == 0:
                raise UserError("Biometric Device is Up/Reachable.")
            else:
                raise UserError("Biometric Device is Down/Unreachable.")
        else:
            if 'unreachable' in str(ping):
                raise UserError("Biometric Device is Down/Unreachable.")
            else:
                raise UserError("Biometric Device is Up/Reachable.")

    def download_attendance_api(self):
        data = {}
        url = "http://103.115.197.23/attendance?ip=%s&port=%s&timeout=%s" % (self.name, self.port_no, self.zk_timeout)
        response = requests.get(url, data=json.dumps(data))
        attendance = json.loads(response.text)
        if attendance:
            zk_attendance = self.env['zk.machine.attendance']
            weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
            date_hour_start = str(date(date.today().year, 3, 13))
            date_hour_end = str(date(date.today().year, 11, 7))
            start_date_check_attendance = str(date.today() - timedelta(days=10))
            for each in attendance:
                dict_date = each['timestamp']
                timedate = parser.parse(dict_date)
                # timedate = datetime.strptime(dict_timestamp, '%Y-%m-%d %H:%M:%S.%f')
                if start_date_check_attendance < str(timedate).split()[0] <= str(date.today()):
                    now_dubai = timedate.astimezone(pytz.timezone('Canada/Eastern'))
                    atten_time1 = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                    if date_hour_start < str(atten_time1).split()[0] < date_hour_end:
                        atten_time = now_dubai - timedelta(hours=1)
                        atten_time = atten_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        atten_time = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                    timendate = str(atten_time).split()
                    name = self.env['hr.employee'].search([('machine_id', '=', each['user_id'])])
                    print(name, "")
                    duplicate_atten_ids = zk_attendance.search(
                        [('employee_id', '=', name.id), ('punching_time', '=', atten_time)])
                    if len(duplicate_atten_ids) > 0:
                        print('if')
                        continue
                    else:
                        print('else')
                        print(len(name) == 1)
                        if len(name) == 1:
                            shift_check = name.employee_shift
                            print('shift_check', shift_check)
                            if shift_check:
                                print('if shift_check', shift_check)
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
                                    print('len(check_record) == 0')
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
                                            'late_time': str(temp_time - shift_start),
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
                                            'late_time': str(temp_time - shift_start),
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
                                            'late_time': str(temp_time - shift_start),
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
                                    print('len(check_record) == 1')
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
                                                check_record.late_time = str(temp_time - shift_start)
                                            elif late_end <= temp_time < short_end:
                                                check_record.status = 'ShortLeave'
                                                check_record.status_leave = 'ShortLeave(paid)'
                                                check_record.late_time = str(temp_time - shift_start)
                                            elif late_end <= temp_time < half_end:
                                                check_record.status = 'HalfLeave'
                                                check_record.late_time = str(temp_time - shift_start)
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
                                        print('hii')
                                        temp_time = datetime.strptime(str(check_record.check_out),
                                                                      '%Y-%m-%d %H:%M:%S').astimezone(
                                            pytz.timezone('Asia/Karachi'))
                                        temp_time = datetime.strptime(str(temp_time),
                                                                      '%Y-%m-%d %H:%M:%S+05:00')
                                        print(temp_time, 'temp_time')
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
                                                print(check_record.out_status, 'PresentOnTime')
                                            elif shift_late_departure_margin <= temp_time:
                                                check_record.out_late_time = False
                                                check_record.out_status = 'PresentOnTime'
                                                print(check_record.out_status, 'PresentOnTime2')
                                            elif shift_late_departure_margin > temp_time >= shift_late_departure:
                                                check_record.out_late_time = str(
                                                    shift_close - temp_time)
                                                check_record.out_status = 'Late'
                                                print(check_record.out_status, 'Late')
                                            elif shift_late_departure > temp_time >= shift_short_departure:
                                                check_record.out_late_time = str(
                                                    shift_close - temp_time)
                                                check_record.out_status = 'ShortLeave'
                                                print(check_record.out_status, 'ShortLeave')
                                            else:
                                                check_record.out_late_time = str(
                                                    shift_close - temp_time)
                                                if check_record.out_status == 'HalfLeave':
                                                    check_record.out_status = 'HalfLeave'
                                                    print(check_record.out_status, 'HalfLeave')
                                                else:
                                                    check_record.out_status = 'Absent'
                                                    print(check_record.out_status, 'Absent')
                            zk_attendance.create({'employee_id': name.id,
                                                  'device_id': each['user_id'],
                                                  'punching_day': timendate[0],
                                                  'attendance_type': str(each['status']),
                                                  # 'location_device': str(machine_ip),
                                                  'punching_time': atten_time})
