# -*- coding: utf-8 -*-
from datetime import datetime, date, time, timedelta
import logging
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import pytz
import time as aztime

from zk import ZK


log = logging.getLogger(__name__)


class ZkMachine(models.Model):
    _name = 'azk.machine'
    
    name = fields.Char(string='Machine', required=True)
    machine_ip = fields.Char("Machine IP/DNS", required=True)
    password = fields.Char('Password', help="Password must be digits.")
    port_num = fields.Integer(string='Port No', required=True)
    serial_num = fields.Char("Serial num", readonly=True)
    timeout = fields.Integer("Connection Timeout", default=10)
    auto_create_employee = fields.Boolean("Auto create employee", help="Automatically create the employee on Odoo if not found", default=False)
    
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    
    last_run_status = fields.Boolean('Machine OK', default=False)
    last_error_msg = fields.Char("Last Error")
    
    @api.onchange('password')
    def _onchange_password(self):
        try:
            val = int(self.password)
        except ValueError:
            raise UserError(_('Password must be digits.'))
        
    @api.model
    def create(self, vals):
        records = super().create(vals)
        for rec in records:
            try:
                val = int(rec.password)
            except ValueError:
                raise UserError(_('Password must be digits.'))
            
        return records
        
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            try:
                val = int(rec.password)
            except ValueError:
                raise UserError(_('Password must be digits.'))
            
        return res
    
    def check_user_id_availabilty(self, user_id, conn=False):
        if not conn:
            conn, _ = self.connect()
            
        machine_users = conn.get_users()
        found = False
        for user in machine_users:
            if user.user_id == user_id:
                found = user
                break
            
        return found
    
    def check_username_exists(self, name, conn=False):
        if not conn:
            conn, _ = self.connect()
            
        machine_users = conn.get_users()
        found = False
        for user in machine_users:
            if user.name.lower() == name.lower():
                found = user
                break
            
        return found
   

    def test_connection(self):
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
            zk = ZK(self.machine_ip, port=self.port_num, password=self.password, timeout=self.timeout, ommit_ping=True)
            conn = zk.connect()
            
            self.last_run_status = True
            self.last_error_msg = None
            self.serial_num = conn.get_serialnumber()
        except Exception as ex:
            log.error("Failed to connect to: %s[%s:%s]", self.name, self.machine_ip, self.port_num, exc_info=1)
            self.last_run_status, self.last_error_msg = False, str(ex)
        
        return conn, zk
    
    def clear_attendance(self):
        try:
            conn, _ = self.connect()
            if conn:
                conn.clear_attendance()
            else:
                log.warn("Failed to connnect to machine: %s on %s:%s", self.name, self.machine_ip, self.port_num)
        except:
            log.error("Failed to clear attendance for machine: %s on %s:%s", self.name, self.machine_ip, self.port_num, exc_info=1)
        finally:
            if conn: conn.disconnect()

    @api.model
    def cron_download(self):
        machines = self.env['azk.machine'].search([])
        for machine in machines :
            try:
                machine.download_attendance()
            except:
                log.error("Failed to download attendance for %s[%s:%s]", machine.name, machine.machine_ip, machine.port_num, exc_info=1)
                
        
    def download_attendance(self):
        """
        Downloads the attendance from the ZK Machine and store them locally and update checin/out.
        It tries to infer the checkin/out via looking if the previous locally stored is checkin and the current date is newer than the checkin date in the DB then it marks it as checkout
        """
        log.info("Downloading attendance started for '%s[%s:%s]'", self.name, self.machine_ip, self.port_num)
        
        AZKAttendance = self.env['azk.machine.attendance']
        HRAttendance = self.env['hr.attendance']
        local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
        
        conn = None
        total_attendance_rec, total_users, total_checkins, total_checkouts = 0, 0, 0, 0
        before = aztime.time()
        try:
            conn, _ = self.connect()
            if conn:
                lst_attendance = conn.get_attendance()
                machine_users = conn.get_users()
                
                users_by_id = dict(map(lambda u: (u.user_id, u), machine_users))
                employees_by_device_id = dict(map(lambda e: (e.device_id, e), self.env['hr.employee'].search([('device_id', 'in', list(map(lambda u:u.user_id, machine_users)))])))
                
                total_attendance_rec, total_users = len(lst_attendance), len(machine_users)
    
                employees_with_attendance = {} #just cache to mininimize queries. Contains employee ID
                
                #get max date imported and only import 3 days back overlapping in order to minimize overhead and speed up import.
                latest_imported = AZKAttendance.search([], order="punching_time desc", limit=1)
                cut_off_date = None
                
                if latest_imported:
                    cut_off_date = latest_imported[0].punching_time - timedelta(days=3)
                    lst_attendance = list(filter(lambda a: a.timestamp > cut_off_date, lst_attendance))
                    
                log.info("Got %s attendance entries and %s users from: %s[%s:%s] importing from: %s -> %s rec to import", total_attendance_rec, len(machine_users), self.name, self.machine_ip, self.port_num, cut_off_date, len(lst_attendance))
                
                for a_rec in sorted(lst_attendance, key=lambda a: a.timestamp):
                    try:
                        atten_time = a_rec.timestamp
                        emp_device_id = str(a_rec.user_id)
                        
                        #TODO why all this shake?
                        local_dt = local_tz.localize(atten_time, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        
                        atten_time_ts = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                        atten_time = fields.Datetime.to_string(atten_time_ts)
                        
                        employee = employees_by_device_id.get(emp_device_id)
                        if not employee:
                            #try to look it in the DB and if found then update the device id
                            employee = self.find_or_create_employee(users_by_id.get(emp_device_id)) if users_by_id.get(emp_device_id) else False
                            employees_by_device_id[emp_device_id] = employee 
                                                    
                        if employee:
                            duplicate_atten_ids = AZKAttendance.search([('device_id', '=', emp_device_id), ('punching_time', '=', atten_time)])
                            
                            if not duplicate_atten_ids:
                                import_status = 'imported'
                                punch_type, _, _ = ZkMachine.resolve_punchtype(a_rec.timestamp, employee)

                                previous_check_in = HRAttendance.search([('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)                                
                                if punch_type == 'checkin':
                                    #get from cache if employee has attendance
                                    if employee.id in employees_with_attendance:
                                        emp_has_attendance_rec = employees_with_attendance[employee.id]
                                    else:
                                        emp_has_attendance_rec = 1 if HRAttendance.search([('employee_id', '=', employee.id)], limit=1) else 0
                                        employees_with_attendance[employee.id] = emp_has_attendance_rec
                                          
                                    #if doesn't have any attendance record or last all are checked out then this is a checkin
                                    if not emp_has_attendance_rec:
                                        HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
                                        employees_with_attendance[employee.id] = 1
                                        total_checkins += 1
                                    #if has checkin records but last one was not a checkin
                                    elif not previous_check_in:
                                        if not HRAttendance.search([('employee_id', '=', employee.id), ('check_in', '=', atten_time)], limit=1):
                                            HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
                                        total_checkins += 1
                                    #if prev checkin is smaller in date then this then close the other as no checkout and create new checkin. NOTE the list of punch should be date sorted ascending 
                                    elif previous_check_in.check_in.date() < atten_time_ts.date():
                                            previous_check_in.write({'check_out': previous_check_in.check_in})
                                            HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
                                            total_checkins += 1
                                    elif previous_check_in.check_in < atten_time_ts and not HRAttendance.search([('employee_id', '=', employee.id), ('check_out', '=', atten_time)], limit=1):
                                        previous_check_in.write({'check_out': atten_time})
                                        total_checkouts += 1
                                    else:
                                        import_status = 'skipped'
                                #if this is a checkout
                                else:
                                    if previous_check_in and previous_check_in.check_in < atten_time_ts and not HRAttendance.search([('employee_id', '=', employee.id), ('check_out', '=', atten_time)], limit=1):
                                        previous_check_in.write({'check_out': atten_time})
                                        total_checkouts += 1
                                    else:
                                        import_status = 'skipped'
         
                                #using the pyzk didn't find a punch in/out thus try to infer it 
                                #if previously checked in but not out and the current date from machine is larger than the previous checkin then then mark this as checkout
#                                 if previous_check_in:
#                                     if previous_check_in.check_in < atten_time_ts:
#                                         previous_check_in.write({'check_out': atten_time})
#                                         total_checkouts += 1
#                                 elif not HRAttendance.search([('employee_id', '=', employee.id), ('check_in', '=', atten_time)], limit=1):
#                                     HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
#                                     total_checkins += 1
                                    
                                AZKAttendance.create({'employee_id': employee.id,
                                                      'device_id': emp_device_id,
                                                      'attendance_type': str(a_rec.status),
                                                      'punch_type': '0' if punch_type == 'checkin' else '1' if punch_type == 'checkout' else None,
                                                      'punching_time': atten_time,
                                                      'import_status': import_status,
                                                      'address_id': self.address_id.id})
                                
                                if import_status == 'skipped':
                                    log.info("Skip updating attendance for %s prev checkin: %s, deteched punch type: '%s'", a_rec, previous_check_in, punch_type)
                                    
                                if ((total_checkins + total_checkouts) % 100) == 0:
                                    log.info("Imported so far: %s checkins and %s checkouts out of %s total", total_checkins, total_checkouts, total_attendance_rec)
    #                         else:
    #                             log.debug("Found duplicate attendance %s on '%s'", a_rec, self.name)
        
                        else:
                            log.info("Skip adding attendance: %s for user: %s. Make sure employee created and device_id set and Auto create employee checked", a_rec, users_by_id.get(emp_device_id))
                    except:
                        log.error("Failed to import attendance '%s' for '%s'", a_rec, self.name, exc_info=1)
            else:
                log.warn("Failed to connect to %s", self.name)
        finally:
            if conn: conn.disconnect()
            
        log.info('Finish import machine %s -> %s attendance records for %s users. Checkins: %s and Checkouts: %s in %0.2fs', self.name, total_attendance_rec, total_users, total_checkins, total_checkouts, aztime.time() - before)
            
        res = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Download status',
                'message': 'Imported %s attendance records for %s users. Checkins: %s and Checkouts: %s' % (total_attendance_rec, total_users, total_checkins, total_checkouts),
                'sticky': False,
                'type': 'success',
            }
        }
        
        return res
    
    @staticmethod
    def resolve_punchtype(punch_time, employee):
        """
        @param punch_time: Datetime for the punch to check if checkin/checkout
        @param employee: employee to search for working hours
        It checks the calendar.attendance for the attendance.employee and based on boundaries it decides if checkin or checkout based on the closest.
        It gets all attendance for the current day of the week for the employee (if not found it takes the first in list)
            - for each entry on that date it checks the closest hour from/to and if close to the hour_from then checkin else checkout.
        
        @return: checkin/out, matching calendar.attendance record, delta in seconds
        """
        
        cal_attendance = employee.resource_calendar_id.attendance_ids.filtered(lambda a: a.dayofweek == str(punch_time.weekday()))
        #if not attendance for given day then get the first one
        if not cal_attendance:
            cal_attendance = employee.resource_calendar_id.attendance_ids.filtered(lambda a: a.dayofweek == employee.resource_calendar_id.attendance_ids[0].dayofweek)
            
        closest_rec, punch_type, t_detla_sec = cal_attendance[0], 'checkin', None
        for c_att in cal_attendance:
            c_from = datetime.combine(punch_time.date(), time(hour=int(c_att.hour_from), minute=int(c_att.hour_from-int(c_att.hour_from))))
            c_to = datetime.combine(punch_time.date(), time(hour=int(c_att.hour_to), minute=int(c_att.hour_to-int(c_att.hour_to))))
            if t_detla_sec is None or abs(c_from - punch_time) < t_detla_sec:
                closest_rec = c_att
                punch_type = 'checkin'
                t_detla_sec = abs(c_from - punch_time)
                
            if abs(c_to - punch_time) < t_detla_sec:
                closest_rec = c_att
                punch_type = 'checkout'
                t_detla_sec = abs(c_from - punch_time)
                
        return punch_type, closest_rec, t_detla_sec
        
    
    def find_or_create_employee(self, user):
        """
        Search employee by name and if found then it updates the device id.
        If not found then it creates a new one
        @requires: hr.employee if found 
        """
        employee = self.env['hr.employee'].search([('name', '=', user.name)], limit=1)
        emp_device_id = str(user.user_id)
        
        if employee:
            employee.write({'device_id': emp_device_id})
            
        if not employee and self.auto_create_employee:
            employee = self.env['hr.employee'].create({'device_id': emp_device_id, 'name': user.name})
        
        return employee

