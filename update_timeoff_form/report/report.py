# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2021 KKNETWORKS (<http://kknetworks.com.pk/>).
#
##############################################################################
import pytz
import time

from odoo import models, fields, api
from odoo.exceptions import ValidationError, Warning
import datetime


class CustomReport(models.AbstractModel):
    _name = "report.update_timeoff_form.hr_leave_balance_report_pdf"

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.leave.balance.report'].browse(docids[0])
        complete_data = []
        if docs.employee_id:
            employees = docs.employee_id
        else:
            employees = self.env['hr.employee'].search([('company_id', '=', self.env.company.id), ('active', '=', True)])
        for employee in employees:
            lines = []
            leaves = []
            sql = """select leave.name, sum(report.number_of_days) from hr_leave_allocation as report
                INNER JOIN hr_leave_type 
                as leave ON leave.id = report.holiday_status_id where date(report.create_date) >= '"""+str(docs.start_date)+"""' 
                and date(report.create_date) <= '"""+str(docs.end_date)+"""' and report.employee_id="""+str(employee.ids[0])+""" and report.state = 'validate' group by leave.name;"""
            self.env.cr.execute(sql)
            allocations_data = self.env.cr.fetchall()
            sql = """select leave.name, sum(report.number_of_days) from hr_leave as report
                INNER JOIN hr_leave_type 
                as leave ON leave.id = report.holiday_status_id where date(report.request_date_to) >= '"""+str(docs.start_date)+"""' 
                and date(report.request_date_to) <= '"""+str(docs.end_date)+"""' and report.employee_id="""+str(employee.ids[0])+""" and report.state = 'validate' group by leave.name;"""
            self.env.cr.execute(sql)
            time_off_data = self.env.cr.fetchall()
            for allocation in allocations_data:
                vals = {
                    'name': allocation[0],
                    'available': allocation[1],
                    'allocated': allocation[1],
                }
                for time_off in time_off_data:
                    if vals['name'] == time_off[0]:
                        vals['available'] -= time_off[1]

                lines.append(vals)
            leaves_tracks = self.env['hr.leave'].search([('employee_id', '=', employee.ids[0]),
                                                         ('state', '=', 'validate')])
            for track in leaves_tracks:
                vals = {
                    "holiday_status_id_name": track.holiday_status_id_name if track.holiday_status_id_name else False,
                    "name": track.name.upper() if track.name else False,
                    "request_date_from": track.request_date_from if track.request_date_from else False,
                    "request_date_to": track.request_date_to if track.request_date_to else False,
                    "number_of_days": track.number_of_days if track.number_of_days else False,
                }
                leaves.append(vals)
            complete_data.append({
                'employee_name': employee.name,
                'employee_code': employee.barcode,
                'employee_department': employee.department_id.name,
                'employee_job': employee.job_id.name,
                'employee_manager': employee.parent_id.name,
                'leave_balance_list': lines,
                'leave_track_list': leaves,
            })
        return {
            'doc_model': 'hr.leave.balance.report',
            'docs': docs,
            'data': data,
            'complete_data': complete_data,
            'print_new_person': self.env.user.login,
            'date_now': datetime.datetime.now(),
        }

