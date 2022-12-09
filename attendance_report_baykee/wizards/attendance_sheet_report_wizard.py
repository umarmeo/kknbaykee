from odoo import models, fields, api, _
from datetime import date, timedelta
import datetime


class AttendanceSheetReportWizard(models.TransientModel):
    _name = 'attendance.sheet.report.wizard'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    type = fields.Selection([
        ('emp', "Employee Wise"),
        ('dpt', "Department Wise")
    ], string="Type")
    employee_ids = fields.Many2many('hr.employee', string="Employee")
    department_ids = fields.Many2many('hr.department', string="Department")

    def export_excel(self):
        self.ensure_one()
        [data] = self.read()
        # company_id = self.env.user.company_id
        start_date = self.start_date
        end_date = self.end_date
        type = self.type
        employee_id = self.employee_ids.ids if self.employee_ids else []
        department_id = self.department_ids.ids if self.department_ids else []
        main = []
        total_days = []
        weekDays = []
        if type == 'emp':
            # for day in range(start.day, mid.days + 1):
            #     total_days.append(day)
            # total_days.sort()
            delta = end_date - start_date
            for i in range(delta.days + 1):
                all_date = start_date + timedelta(days=i)
                tt = str(all_date.day) + '-' + str(all_date.month) + '-' + str(all_date.year)
                total_days.append(tt)
                shortname = all_date.strftime('%a')
                weekDays.append(shortname)
            print(total_days)
            employee = self.env['hr.employee'].search([('id', 'in', employee_id)])
            for emp in employee:
                days = []
                status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                  ('status', '=', 'Absent'),
                                                                  ('out_status', '!=', 'Absent'),
                                                                  ('current_shiftatt_date', '>=', start_date),
                                                                  ('current_shiftatt_date', '<=', end_date)])
                out_status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                      ('status', '!=', 'Absent'),
                                                                      ('out_status', '=', 'Absent'),
                                                                      ('current_shiftatt_date', '>=',
                                                                       start_date),
                                                                      ('current_shiftatt_date', '<=', end_date)])
                both_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                ('status', '=', 'Absent'),
                                                                ('out_status', '=', 'Absent'),
                                                                ('current_shiftatt_date', '>=',
                                                                 start_date),
                                                                ('current_shiftatt_date', '<=', end_date)])
                total_absent = len(status_absent) + len(out_status_absent) + len(both_absent)
                status_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                ('status', '=', 'Late'),
                                                                ('out_status', '!=', 'Late'),
                                                                ('current_shiftatt_date', '>=', start_date),
                                                                ('current_shiftatt_date', '<=', end_date)])
                out_status_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                    ('status', '!=', 'Late'),
                                                                    ('out_status', '=', 'Late'),
                                                                    ('current_shiftatt_date', '>=',
                                                                     start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])
                both_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                              ('status', '=', 'Late'),
                                                              ('out_status', '=', 'Late'),
                                                              ('current_shiftatt_date', '>=',
                                                               start_date),
                                                              ('current_shiftatt_date', '<=', end_date)])
                total_late = len(status_late) + len(out_status_late) + len(both_late)
                status_short = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                 ('status', '=', 'ShortLeave'),
                                                                 ('out_status', 'not in', ('ShortLeave', 'Absent')),
                                                                 ('current_shiftatt_date', '>=', start_date),
                                                                 ('current_shiftatt_date', '<=', end_date)])
                out_status_short = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                     ('status', 'not in', ('ShortLeave', 'Absent')),
                                                                     ('out_status', '=', 'ShortLeave'),
                                                                     ('current_shiftatt_date', '>=',
                                                                      start_date),
                                                                     ('current_shiftatt_date', '<=', end_date)])
                both_short = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                               ('status', '=', 'ShortLeave'),
                                                               ('out_status', '=', 'ShortLeave'),
                                                               ('current_shiftatt_date', '>=',
                                                                start_date),
                                                               ('current_shiftatt_date', '<=', end_date)])
                total_short = len(status_short) + len(out_status_short) + len(both_short)
                status_half = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                ('status', '=', 'HalfLeave'),
                                                                ('out_status', 'not in', ('HalfLeave', 'Absent')),
                                                                ('current_shiftatt_date', '>=', start_date),
                                                                ('current_shiftatt_date', '<=', end_date)])
                out_status_half = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                    ('status', 'not in', ('HalfLeave', 'Absent')),
                                                                    ('out_status', '=', 'HalfLeave'),
                                                                    ('current_shiftatt_date', '>=', start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])
                both_half = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                              ('status', '=', 'HalfLeave'),
                                                              ('out_status', '=', 'HalfLeave'),
                                                              ('current_shiftatt_date', '>=', start_date),
                                                              ('current_shiftatt_date', '<=', end_date)])
                total_half = len(status_half) + len(out_status_half) + len(both_half)
                status_leave = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                 ('status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                   'BloodRelationDeathLeave')),
                                                                 ('out_status', 'not in', ('PaidLeave', 'MarriageLeave',
                                                                                           'BloodRelationDeathLeave',
                                                                                           'Absent')),
                                                                 ('current_shiftatt_date', '>=', start_date),
                                                                 ('current_shiftatt_date', '<=', end_date)])
                out_status_leave = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                     ('status', 'not in', ('PaidLeave', 'MarriageLeave',
                                                                                           'BloodRelationDeathLeave',
                                                                                           'Absent')),
                                                                     ('out_status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                           'BloodRelationDeathLeave')),
                                                                     ('current_shiftatt_date', '>=', start_date),
                                                                     ('current_shiftatt_date', '<=', end_date)])
                both_leave = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                               ('status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                 'BloodRelationDeathLeave')),
                                                               ('out_status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                     'BloodRelationDeathLeave')),
                                                               ('current_shiftatt_date', '>=', start_date),
                                                               ('current_shiftatt_date', '<=', end_date)])
                total_leave = len(status_leave) + len(out_status_leave) + len(both_leave)
                status_present = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                   ('status', '=', 'PresentOnTime'),
                                                                   ('out_status', '!=', 'PresentOnTime'),
                                                                   ('current_shiftatt_date', '>=', start_date),
                                                                   ('current_shiftatt_date', '<=', end_date)])
                out_status_present = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                       ('status', '!=', 'PresentOnTime'),
                                                                       ('out_status', '=', 'PresentOnTime'),
                                                                       ('current_shiftatt_date', '>=', start_date),
                                                                       ('current_shiftatt_date', '<=', end_date)])
                both_present = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                 ('status', '=', 'PresentOnTime'),
                                                                 ('out_status', '=', 'PresentOnTime'),
                                                                 ('current_shiftatt_date', '>=',
                                                                  start_date),
                                                                 ('current_shiftatt_date', '<=', end_date)])
                total_present = len(status_present) + len(out_status_present) + len(both_present)
                attendance = self.env['hr.attendance'].search(
                    [('employee_id', '=', emp.id), ('current_shiftatt_date', '>=', start_date),
                     ('current_shiftatt_date', '<=', end_date)], order="current_shiftatt_date asc")
                status = ''
                out_status = ''
                for st in attendance:
                    if st.status != 'RestDay':
                        if st.status == 'PresentOnTime':
                            status = 'P'
                        elif st.status == 'Late':
                            status = 'L'
                        elif st.status == 'ShortLeave':
                            status = 'SL'
                        elif st.status == 'HalfLeave':
                            status = 'HL'
                        elif st.status in ('PaidLeave', 'MarriageLeave', 'BloodRelationDeathLeave'):
                            status = "LEAVE"
                        elif st.status == 'Absent':
                            status = 'A'

                        if st.out_status == 'PresentOnTime':
                            out_status = 'P'
                        elif st.out_status == 'Late':
                            out_status = 'L'
                        elif st.out_status == 'ShortLeave':
                            out_status = 'SL'
                        elif st.out_status == 'HalfLeave':
                            out_status = 'HL'
                        elif st.status in ('PaidLeave', 'MarriageLeave', 'BloodRelationDeathLeave'):
                            status = "LEAVE"
                        elif st.out_status == 'Absent':
                            out_status = 'A'
                        status1 = status + ',' + out_status
                    else:
                        status1 = 'SUN'
                    days.append(status1)
                main.append({
                    'employee': emp.name,
                    'design': emp.job_title,
                    'dept': emp.department_id.name,
                    'days': days,
                    'total_no_days': len(total_days),
                    'total_absent': total_absent,
                    'total_late': total_late,
                    'total_short': total_short,
                    'total_half': total_half,
                    'total_leave': total_leave,
                    'total_present': total_present,
                })
        if type == 'dpt':
            delta = end_date - start_date
            for i in range(delta.days + 1):
                all_date = start_date + timedelta(days=i)
                tt = str(all_date.day) + '-' + str(all_date.month) + '-' + str(all_date.year)
                total_days.append(tt)
                shortname = all_date.strftime('%a')
                weekDays.append(shortname)
            department = self.env['hr.department'].search([('id', 'in', department_id)])
            for dept in department:
                employee = self.env['hr.employee'].search([('department_id', '=', dept.id)])
                for emp in employee:
                    days = []
                    status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                      ('status', '=', 'Absent'),
                                                                      ('out_status', '!=', 'Absent'),
                                                                      ('current_shiftatt_date', '>=', start_date),
                                                                      ('current_shiftatt_date', '<=', end_date)])
                    out_status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                          ('status', '!=', 'Absent'),
                                                                          ('out_status', '=', 'Absent'),
                                                                          ('current_shiftatt_date', '>=',
                                                                           start_date),
                                                                          ('current_shiftatt_date', '<=', end_date)])
                    both_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                    ('status', '=', 'Absent'),
                                                                    ('out_status', '=', 'Absent'),
                                                                    ('current_shiftatt_date', '>=',
                                                                     start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])
                    total_absent = len(status_absent) + len(out_status_absent) + len(both_absent)
                    status_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                    ('status', '=', 'Late'),
                                                                    ('out_status', '!=', 'Late'),
                                                                    ('current_shiftatt_date', '>=', start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])
                    out_status_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                        ('status', '!=', 'Late'),
                                                                        ('out_status', '=', 'Late'),
                                                                        ('current_shiftatt_date', '>=',
                                                                         start_date),
                                                                        ('current_shiftatt_date', '<=', end_date)])
                    both_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                  ('status', '=', 'Late'),
                                                                  ('out_status', '=', 'Late'),
                                                                  ('current_shiftatt_date', '>=',
                                                                   start_date),
                                                                  ('current_shiftatt_date', '<=', end_date)])
                    total_late = len(status_late) + len(out_status_late) + len(both_late)
                    status_short = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                     ('status', '=', 'ShortLeave'),
                                                                     ('out_status', 'not in', ('ShortLeave', 'Absent')),
                                                                     ('current_shiftatt_date', '>=', start_date),
                                                                     ('current_shiftatt_date', '<=', end_date)])
                    out_status_short = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                         ('status', 'not in', ('ShortLeave', 'Absent')),
                                                                         ('out_status', '=', 'ShortLeave'),
                                                                         ('current_shiftatt_date', '>=',
                                                                          start_date),
                                                                         ('current_shiftatt_date', '<=', end_date)])
                    both_short = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                   ('status', '=', 'ShortLeave'),
                                                                   ('out_status', '=', 'ShortLeave'),
                                                                   ('current_shiftatt_date', '>=',
                                                                    start_date),
                                                                   ('current_shiftatt_date', '<=', end_date)])
                    total_short = len(status_short) + len(out_status_short) + len(both_short)
                    status_half = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                    ('status', '=', 'HalfLeave'),
                                                                    ('out_status', 'not in', ('HalfLeave', 'Absent')),
                                                                    ('current_shiftatt_date', '>=', start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])
                    out_status_half = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                        ('status', 'not in', ('HalfLeave', 'Absent')),
                                                                        ('out_status', '=', 'HalfLeave'),
                                                                        ('current_shiftatt_date', '>=', start_date),
                                                                        ('current_shiftatt_date', '<=', end_date)])
                    both_half = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                  ('status', '=', 'HalfLeave'),
                                                                  ('out_status', '=', 'HalfLeave'),
                                                                  ('current_shiftatt_date', '>=', start_date),
                                                                  ('current_shiftatt_date', '<=', end_date)])
                    total_half = len(status_half) + len(out_status_half) + len(both_half)
                    status_leave = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                     ('status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                       'BloodRelationDeathLeave')),
                                                                     ('out_status', 'not in', ('PaidLeave', 'MarriageLeave',
                                                                                               'BloodRelationDeathLeave',
                                                                                               'Absent')),
                                                                     ('current_shiftatt_date', '>=', start_date),
                                                                     ('current_shiftatt_date', '<=', end_date)])
                    out_status_leave = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                         ('status', 'not in', ('PaidLeave', 'MarriageLeave',
                                                                                               'BloodRelationDeathLeave',
                                                                                               'Absent')),
                                                                         ('out_status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                               'BloodRelationDeathLeave')),
                                                                         ('current_shiftatt_date', '>=', start_date),
                                                                         ('current_shiftatt_date', '<=', end_date)])
                    both_leave = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                   ('status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                     'BloodRelationDeathLeave')),
                                                                   ('out_status', 'in', ('PaidLeave', 'MarriageLeave',
                                                                                         'BloodRelationDeathLeave')),
                                                                   ('current_shiftatt_date', '>=', start_date),
                                                                   ('current_shiftatt_date', '<=', end_date)])
                    total_leave = len(status_leave) + len(out_status_leave) + len(both_leave)
                    status_present = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                       ('status', '=', 'PresentOnTime'),
                                                                       ('out_status', '!=', 'PresentOnTime'),
                                                                       ('current_shiftatt_date', '>=', start_date),
                                                                       ('current_shiftatt_date', '<=', end_date)])
                    out_status_present = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                           ('status', '!=', 'PresentOnTime'),
                                                                           ('out_status', '=', 'PresentOnTime'),
                                                                           ('current_shiftatt_date', '>=', start_date),
                                                                           ('current_shiftatt_date', '<=', end_date)])
                    both_present = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                     ('status', '=', 'PresentOnTime'),
                                                                     ('out_status', '=', 'PresentOnTime'),
                                                                     ('current_shiftatt_date', '>=',
                                                                      start_date),
                                                                     ('current_shiftatt_date', '<=', end_date)])
                    total_present = len(status_present) + len(out_status_present) + len(both_present)
                    attendance = self.env['hr.attendance'].search(
                        [('employee_id', '=', emp.id), ('current_shiftatt_date', '>=', start_date),
                         ('current_shiftatt_date', '<=', end_date)], order="current_shiftatt_date asc")
                    status = ''
                    out_status = ''
                    for st in attendance:
                        if st.status != 'RestDay':
                            if st.status == 'PresentOnTime':
                                status = 'P'
                            elif st.status == 'Late':
                                status = 'L'
                            elif st.status == 'ShortLeave':
                                status = 'SL'
                            elif st.status == 'HalfLeave':
                                status = 'HL'
                            elif st.status in ('PaidLeave', 'MarriageLeave', 'BloodRelationDeathLeave'):
                                status = "LEAVE"
                            elif st.status == 'Absent':
                                status = 'A'

                            if st.out_status == 'PresentOnTime':
                                out_status = 'P'
                            elif st.out_status == 'Late':
                                out_status = 'L'
                            elif st.out_status == 'ShortLeave':
                                out_status = 'SL'
                            elif st.out_status == 'HalfLeave':
                                out_status = 'HL'
                            elif st.status in ('PaidLeave', 'MarriageLeave', 'BloodRelationDeathLeave'):
                                status = "LEAVE"
                            elif st.out_status == 'Absent':
                                out_status = 'A'
                            status1 = status + ',' + out_status
                        else:
                            status1 = 'SUN'
                        days.append(status1)
                    main.append({
                        'employee': emp.name,
                        'design': emp.job_title,
                        'dept': emp.department_id.name,
                        'days': days,
                        'total_no_days': len(total_days),
                        'total_absent': total_absent,
                        'total_late': total_late,
                        'total_short': total_short,
                        'total_half': total_half,
                        'total_leave': total_leave,
                        'total_present': total_present,
                    })
        datas = {
            'ids': [],
            'model': 'attendance.sheet.report.wizard',
            'form': data,
            'main': main,
            'weekDays': weekDays,
            'total_days': total_days,
            'type': type,
        }

        return self.env.ref('attendance_report_baykee.action_attendance_sheet_report_xlsx').with_context(
            landscape=False).report_action(self, data=datas, config=False)
