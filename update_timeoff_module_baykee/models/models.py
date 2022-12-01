# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

import logging, pytz
from collections import namedtuple
from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC
from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

# Used to agglomerate the attendances in order to find the hour_from and hour_to
# See _onchange_request_parameters
DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period, week_type')


class update_timeoff_form(models.Model):
    _inherit = 'hr.leave'

    holiday_status_id_name = fields.Char(related='holiday_status_id.name')

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        mapped_days = self.mapped('holiday_status_id').get_employees_days(self.mapped('employee_id').ids)
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(
                    leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                pass

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        current_employee = self.env.user.employee_id
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.holiday_status_id.leave_validation_type

            if not is_manager and state != 'confirm':
                if state == 'draft':
                    if holiday.state == 'refuse':
                        raise UserError(_('Only a Leave Manager can reset a refused leave.'))
                    if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
                        raise UserError(_('Only a Leave Manager can reset a started leave.'))
                    if holiday.employee_id != current_employee:
                        raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                else:
                    if val_type == 'no_validation' and current_employee == holiday.employee_id:
                        continue
                    # use ir.rule based first access check: department, members, ... (see security.xml)
                    holiday.check_access_rule('write')

                    # # This handles states validate1 validate and refuse
                    # if holiday.employee_id == current_employee:
                    #     raise UserError(_('Only a Leave Manager can approve/refuse its own requests.'))

                    if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager') and holiday.holiday_type == 'employee':
                        if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
                            raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))

    def _validate_leave_request(self):
        """ Validate time off requests (holiday_type='employee')
        by creating a calendar event and a resource time off. """
        holidays = self.filtered(lambda request: request.holiday_type == 'employee')
        holidays._create_resource_leave()
        meeting_holidays = holidays.filtered(lambda l: l.holiday_status_id.create_calendar_meeting)
        for leave in self:
            if leave.holiday_status_id.name == 'Marriage Leaves':
                status = 'MarriageLeave'
                status1 = 'MarriageLeave'
            elif leave.holiday_status_id.name == 'Unpaid Leaves':
                status = 'SickLeave'
                status1 = 'SickLeave'
            elif leave.holiday_status_id.name == 'Blood Relation Death Leaves':
                status = 'BloodRelationDeathLeave'
                status1 = 'BloodRelationDeathLeave'
            elif leave.holiday_status_id.name == 'Unpaid Leaves':
                status = 'UnpaidLeave'
                status1 = 'UnpaidLeave'
            else:
                status = 'PaidLeave'
                status1 = 'PaidLeave'
            if leave.holiday_type == 'employee':
                start_date = leave.request_date_from
                end_date = leave.request_date_to
                delta = timedelta(days=1)
                while start_date <= end_date:
                    date_hour_start = str(date(start_date.year, 3, 13))
                    date_hour_end = str(date(start_date.year, 11, 7))
                    check_in = datetime(start_date.year, start_date.month,
                                                 start_date.day) + timedelta(
                        hours=leave.employee_id.employee_shift.shift_start)
                    now_dubai = check_in.astimezone(pytz.timezone('Canada/Eastern'))
                    # if leave.employee_id.new_shift_type.shift_type == 'Night':
                    #     now_dubai += timedelta(days=1)
                    atten_time1 = now_dubai.strftime("%Y-%m-%d %H:%M:%S")
                    if date_hour_start < str(atten_time1).split()[0] < date_hour_end:
                        check_in = now_dubai - timedelta(hours=1)
                        check_in = check_in.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        check_in = now_dubai.strftime("%Y-%m-%d %H:%M:%S")

                    check_record = self.env['hr.attendance'].search([('employee_id', '=', leave.employee_id.id),
                                                                     ('current_shiftatt_date', '=', start_date)])
                    if len(check_record) == 1:
                        if check_record.status != 'RestDay':
                            if holidays.name.find("Auto Short Leave Deduction") == -1:
                                if leave.report_note:
                                    payroll_start_date = start_date.replace(day=1)
                                    payroll_end_date = start_date.replace(day=1) + relativedelta(months=1) - timedelta(
                                        days=1)
                                    payroll_check = self.env['hr.payslip.run'].search(
                                        [('date_start', '=', payroll_start_date),
                                         ('date_end', '=', payroll_end_date),
                                         ('state', '=', 'close')])
                                    contracts = self.env['hr.contract'].search(
                                        [('employee_id', '=', self.employee_id.id)], limit=1)
                                    if leave.report_note == '3':
                                        if len(payroll_check) == 1 and (check_record.status == 'Absent' or check_record.out_status == 'Absent') and len(contracts) == 1:
                                            one_day_salary = round(contracts.gross_finals / payroll_end_date.day,0)
                                            contracts.arrears += one_day_salary
                                            body = (
                                                    _("Added arrears for the absent of date:- %s - amount %s after applying leave") % (str(start_date), str(one_day_salary)))
                                            contracts.message_post(body=body)
                                        check_record.status = status
                                        check_record.out_status = status
                                        check_record.late_time = False
                                        check_record.out_late_time = False
                                    elif leave.report_note == '1':
                                        if len(payroll_check) == 1 and (check_record.status == 'Absent' and check_record.out_status != 'Absent'):
                                            one_day_salary = round(contracts.gross_finals / payroll_end_date.day,0)
                                            contracts.arrears += one_day_salary
                                            body = (
                                                    _("Added arrears for the absent of date:- %s - amount %s after applying leave") % (str(start_date), str(one_day_salary)))
                                            contracts.message_post(body=body)

                                        check_record.late_time = False
                                        check_record.status = status
                                    elif leave.report_note == '2':
                                        if len(payroll_check) == 1 and (check_record.status != 'Absent' and check_record.out_status == 'Absent'):
                                            one_day_salary = round(contracts.gross_finals / payroll_end_date.day,0)
                                            contracts.arrears += one_day_salary
                                            body = (
                                                    _("Added arrears for the absent of date:- %s - amount %s after applying leave") % (str(start_date), str(one_day_salary)))
                                            contracts.message_post(body=body)
                                        check_record.out_late_time = False
                                        check_record.out_status = status
                            check_record.status_leave = status1
                        if leave.holiday_status_id.name == 'Gazette Holiday' and check_record.worked_hours >= 8:
                            compensatory_type = self.env['hr.leave.type'].search([('name', '=', 'Compensatory Days')])
                            vals = self.env['hr.leave.employee'].create({
                                'name': 'Auto System Generated CPL against ' + str(start_date) + ' Working ON Gazette '
                                                                                                 'Day',
                                'leave_type': compensatory_type.id,
                                'employee_id': leave.employee_id.id,
                                'department_id': leave.employee_id.department_id.id,
                                'types': 'Allocation',
                                'state': 'Draft',
                                'number_of_days': 1,
                            })
                            vals.request_approved_allocation()
                    else:
                        att_vals = {
                            'employee_id': leave.employee_id.id,
                            'new_shift': leave.employee_id.employee_shift.id if leave.employee_id.employee_shift else False,
                            'current_shiftatt_date': start_date,
                            'check_in': check_in,
                            'check_out': check_in,
                            'status_leave': status1,
                        }
                        if leave.report_note:
                            if leave.report_note == '3':
                                att_vals['status'] = status
                                att_vals['out_status'] = status
                            elif leave.report_note == '1':
                                att_vals['out_status'] = 'Absent'
                                att_vals['status'] = status
                            elif leave.report_note == '2':
                                att_vals['status'] = 'Absent'
                                att_vals['out_status'] = status
                            if leave.report_note != '0':
                                self.env['hr.attendance'].create(att_vals)
                    if leave.holiday_status_id.name == 'Official Leaves':
                        weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
                        rest_day = []
                        for rest in leave.employee_id.rest_days:
                            rest_day.append(weekDays[int(rest.id) - 1])
                        if start_date.strftime("%A") in rest_day:
                            compensatory_type = self.env['hr.leave.type'].search([('name', '=', 'Compensatory Days')])
                            vals = self.env['hr.leave.employee'].create({
                                'name': 'Auto System Generated CPL against Official Leave ' + str(start_date) + ' ON Rest '
                                                                                                 'Day',
                                'leave_type': compensatory_type.id,
                                'employee_id': leave.employee_id.id,
                                'department_id': leave.employee_id.department_id.id,
                                'types': 'Allocation',
                                'state': 'Draft',
                                'number_of_days': 1,
                            })
                            vals.request_approved_allocation()
                    start_date += delta
            elif leave.holiday_type == 'department':
                employeesearch = self.env['hr.employee'].search([('department_id', '=', leave.department_id.id)])
                for employee in employeesearch:
                    start_date = leave.request_date_from
                    end_date = leave.request_date_to
                    delta = timedelta(days=1)
                    while start_date <= end_date:
                        date_hour_start = str(date(start_date.year, 3, 13))
                        date_hour_end = str(date(start_date.year, 11, 7))
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
                        att_vals = {
                            'employee_id': employee.id,
                            'current_shiftatt_date': start_date,
                            'new_shift': employee.employee_shift.id if employee.employee_shift else False,
                            'check_in': check_in,
                            'check_out': check_in,
                            'status': status,
                            'out_status': status,
                            'status_leave': status1,
                            'late_time': False,
                        }
                        check_record = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('current_shiftatt_date', '=', start_date)])
                        if len(check_record) == 1:
                            if check_record.status != 'RestDay':
                                # check_record.check_in = check_in
                                # check_record.check_out = check_in
                                check_record.status = status
                                check_record.out_status = status
                                check_record.status_leave = status1
                                check_record.late_time = False
                                check_record.out_late_time = False
                            if leave.holiday_status_id.name == 'Gazette Holiday' and check_record.worked_hours >= 8:
                                compensatory_type = self.env['hr.leave.type'].search(
                                    [('name', '=', 'Compensatory Days')])
                                vals = self.env['hr.leave.employee'].create({
                                    'name': 'Auto System Generated CPL against ' + str(
                                        start_date) + ' Working ON Gazette '
                                                      'Day',
                                    'leave_type': compensatory_type.id,
                                    'employee_id': employee.id,
                                    'department_id': employee.department_id.id,
                                    'types': 'Allocation',
                                    'state': 'Draft',
                                    'number_of_days': 1,
                                })
                                vals.request_approved_allocation()
                        else:
                            self.env['hr.attendance'].create(att_vals)
                        start_date += delta
            elif leave.holiday_type == 'company':
                employeesearch = self.env['hr.employee'].search([('address_id', '=', leave.mode_company_id.partner_id.id)])
                for employee in employeesearch:
                    start_date = leave.request_date_from
                    end_date = leave.request_date_to.date()
                    delta = timedelta(days=1)
                    while start_date <= end_date:
                        date_hour_start = str(date(start_date.year, 3, 13))
                        date_hour_end = str(date(start_date.year, 11, 7))
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
                        att_vals = {
                            'employee_id': employee.id,
                            'current_shiftatt_date': start_date,
                            'new_shift': employee.employee_shift.id if employee.employee_shift else False,
                            'check_in': check_in,
                            'check_out': check_in,
                            'status': status,
                            'out_status': status,
                            'status_leave': status1,
                            'late_time': False,
                        }
                        check_record = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('current_shiftatt_date', '=', start_date)])
                        if len(check_record) == 1:
                            if check_record.status != 'RestDay':
                                # check_record.check_in = check_in
                                # check_record.check_out = check_in
                                check_record.status = status
                                check_record.out_status = status
                                check_record.status_leave = status1
                                check_record.late_time = False
                            if leave.holiday_status_id.name == 'Gazette Holiday' and check_record.worked_hours >= 8:
                                compensatory_type = self.env['hr.leave.type'].search(
                                    [('name', '=', 'Compensatory Days')])
                                vals = self.env['hr.leave.employee'].create({
                                    'name': 'Auto System Generated CPL against ' + str(
                                        start_date) + ' Working ON Gazette '
                                                      'Day',
                                    'leave_type': compensatory_type.id,
                                    'employee_id': employee.id,
                                    'department_id': employee.department_id.id,
                                    'types': 'Allocation',
                                    'state': 'Draft',
                                    'number_of_days': 1,
                                })
                                vals.request_approved_allocation()
                        else:
                            self.env['hr.attendance'].create(att_vals)
                        start_date += delta
            elif leave.holiday_type == 'category':
                pass


class LeaveReportUpdate(models.Model):
    _inherit = "hr.leave.report"

    request_date_from = fields.Date('Start Date', readonly=True)
    request_date_to = fields.Date('End Date', readonly=True)
#
#     def init(self):
#         tools.drop_view_if_exists(self._cr, 'hr_leave_report')
#
#         self._cr.execute("""
#             CREATE or REPLACE view hr_leave_report as (
#                 SELECT row_number() over(ORDER BY leaves.employee_id) as id,
#                 leaves.employee_id as employee_id, leaves.name as name,
#                 leaves.number_of_days as number_of_days, leaves.leave_type as leave_type,
#                 leaves.category_id as category_id, leaves.department_id as department_id,
#                 leaves.holiday_status_id as holiday_status_id, leaves.state as state,
#                 leaves.holiday_type as holiday_type, leaves.date_from as date_from,
#                 leaves.date_to as date_to, leaves.payslip_status as payslip_status,
#                 leaves.request_date_to as request_date_to, leaves.request_date_from as request_date_from
#                 from (select
#                     allocation.employee_id as employee_id,
#                     allocation.name as name,
#                     allocation.number_of_days as number_of_days,
#                     allocation.category_id as category_id,
#                     allocation.department_id as department_id,
#                     allocation.holiday_status_id as holiday_status_id,
#                     allocation.state as state,
#                     allocation.holiday_type,
#                     null as date_from,
#                     null as date_to,
#                     FALSE as payslip_status,
#                     null as request_date_to,
#                     null as request_date_from,
#                     'allocation' as leave_type
#                 from hr_leave_allocation as allocation
#                 union all select
#                     request.employee_id as employee_id,
#                     request.name as name,
#                     (request.number_of_days * -1) as number_of_days,
#                     request.category_id as category_id,
#                     request.department_id as department_id,
#                     request.holiday_status_id as holiday_status_id,
#                     request.state as state,
#                     request.holiday_type,
#                     request.date_from as date_from,
#                     request.date_to as date_to,
#                     request.payslip_status as payslip_status,
#                     request.request_date_to as request_date_to,
#                     request.request_date_from as request_date_from,
#                     'request' as leave_type
#                 from hr_leave as request) leaves
#             );
#         """)


class HRLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    leave_type_days = fields.Selection([('monthly', 'monthly'), ('annually', 'annually')], string="Leave Days Type", required=True)
    days_annual_leave = fields.Integer('Annual Days')
    days_monthly_leave = fields.Integer('Monthly Days')
    no_of_year = fields.Integer('No of Years', default=1)

    @api.onchange('leave_type_days')
    def _onchange_leave_type_days(self):
        self.days_monthly_leave = 0
        self.days_annual_leave = 0
