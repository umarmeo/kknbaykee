from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging
import datetime, calendar

_logger = logging.getLogger(__name__)


class DepartWisePayableSummaryReportTemplate(models.AbstractModel):
    _name = 'report.payroll_reports_baykee.payable_summary_report_temp'
    _description = 'Department Wise Payable Days Summary Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['depart.payable.summary.report.wizard'].browse(docids[0])
        company_id = self.env.user.company_id
        month = docs.month
        year = docs.year
        department_id = docs.department_ids.ids if docs.department_ids else []
        department = self.env['hr.department'].search([('id', 'in', department_id)])
        data_temp = []
        for dept in department:
            temp = []
            employee = self.env['hr.employee'].search([('department_id', '=', dept.id)])
            for emp in employee:
                year1 = int(year)
                month1 = int(month)
                days_in_month = calendar.monthrange(year1, month1)[1]
                date_start = datetime.datetime(year1, month1, 1)
                date_end = datetime.datetime(year1, month1, days_in_month)
                date_avg = date_end - date_start
                total_days = date_avg.days + 1
                status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                  ('status', '=', 'Absent'),
                                                                  ('out_status', '!=', 'Absent'),
                                                                  ('current_shiftatt_date', '>=', date_start),
                                                                  ('current_shiftatt_date', '<=', date_end)])
                out_status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                      ('status', '!=', 'Absent'),
                                                                      ('out_status', '=', 'Absent'),
                                                                      ('current_shiftatt_date', '>=',
                                                                       date_start),
                                                                      ('current_shiftatt_date', '<=', date_end)])
                both_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                ('status', '=', 'Absent'),
                                                                ('out_status', '=', 'Absent'),
                                                                ('current_shiftatt_date', '>=',
                                                                 date_start),
                                                                ('current_shiftatt_date', '<=', date_end)])
                total_absent = len(status_absent) + len(out_status_absent) + len(both_absent)
                status_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                ('status', '=', 'Late'),
                                                                ('out_status', '!=', 'Late'),
                                                                ('current_shiftatt_date', '>=', date_start),
                                                                ('current_shiftatt_date', '<=', date_end)])
                out_status_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                    ('status', '!=', 'Late'),
                                                                    ('out_status', '=', 'Late'),
                                                                    ('current_shiftatt_date', '>=',
                                                                     date_start),
                                                                    ('current_shiftatt_date', '<=', date_end)])
                both_late = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                              ('status', '=', 'Late'),
                                                              ('out_status', '=', 'Late'),
                                                              ('current_shiftatt_date', '>=',
                                                               date_start),
                                                              ('current_shiftatt_date', '<=', date_end)])
                total_late = len(status_late) + len(out_status_late) + len(both_late)
                total_late_process = 0
                if total_late >= 4:
                    total_late_process = int(total_late / 4)
                vals = {
                    'employee': emp.name,
                    'designation': emp.job_title,
                    'working_days': total_days,
                    'salary_days': total_days,
                    'total_late': total_late,
                    'total_absent': total_absent,
                    'total_payable': total_days - total_late_process - total_absent,
                }
                temp.append(vals)
            temp2 = temp
            data_temp.append(
                [dept.name, temp2, month, year])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
