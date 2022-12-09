from odoo import api, fields, models
import datetime


class SalarySummaryReportTemplate(models.AbstractModel):
    _name = 'report.payroll_reports_baykee.salary_summary_report'
    _description = 'Salary Summary Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['salary.summary.report.wizard'].browse(docids[0])
        company_id = self.env.user.company_id
        month = docs.month
        year = docs.year
        type = docs.type
        employee_id = docs.employee_ids.ids if docs.employee_ids else []
        department_id = docs.department_ids.ids if docs.department_ids else []
        if type == 'emp':
            employee = self.env['hr.employee'].search([('id', 'in', employee_id)])
            for emp in employee:
                payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', emp.id), ('month', '=', month), ('year', '=', year)])
                total_days = 0
                total_absent = 0
                for slip in payslip:
                    date_start = slip.date_from
                    date_end = slip.date_to
                    date_avg = date_end - date_start
                    total_days = date_avg.days + 1
                    if emp.contract_id.date_start > date_start:
                        temp_start_date = emp.joining_date
                    else:
                        temp_start_date = date_start
                    status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                      ('status', '=', 'Absent'),
                                                                      ('out_status', '!=', 'Absent'),
                                                                      ('current_shiftatt_date', '>=', temp_start_date),
                                                                      ('current_shiftatt_date', '<=', date_end)])
                    out_status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                          ('status', '!=', 'Absent'),
                                                                          ('out_status', '=', 'Absent'),
                                                                          ('current_shiftatt_date', '>=',
                                                                           temp_start_date),
                                                                          ('current_shiftatt_date', '<=', date_end)])
                    total_absent = len(status_absent) + len(out_status_absent)
                payslip_line = self.env['hr.payslip.line'].search(
                    [('employee_id', '=', emp.id), ('slip_id.month', '=', month), ('slip_id.year', '=', year)])
                temp = []
                basic = 0
                gross = 0
                net = 0
                tax = 0
                adv_sal = 0
                loan = 0
                mobile_bill = 0
                absent_deduction = 0
                late_deduction = 0
                short_leave_deduction = 0
                half_leave_deduction = 0
                for line in payslip_line:
                    basics = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Basic Salary")])
                    basic += basics.amount
                    grosses = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Gross Salary")])
                    gross += grosses.amount
                    nets = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Net Salary")])
                    net += nets.amount
                    taxs = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Tax")])
                    tax += taxs.amount
                    adv_sals = self.env['hr.payslip.line'].search(
                        [('id', '=', line.id), ('name', '=', "Advance Salary")])
                    adv_sal += adv_sals.amount
                    loans = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Loan")])
                    loan += loans.amount
                    mobile_bills = self.env['hr.payslip.line'].search(
                        [('id', '=', line.id), ('name', '=', "Mobile Bill")])
                    mobile_bill += mobile_bills.amount
                    absent_deductions = self.env['hr.payslip.line'].search(
                        [('id', '=', line.id), ('name', '=', "Absent Deductions")])
                    absent_deduction += absent_deductions.amount
                    late_deductions = self.env['hr.payslip.line'].search(
                        [('id', '=', line.id), ('name', '=', "Late Deductions")])
                    late_deduction = late_deductions.amount
                    short_leave_deductions = self.env['hr.payslip.line'].search(
                        [('id', '=', line.id), ('name', '=', "Short Leave Deductions")])
                    short_leave_deduction += short_leave_deductions.amount
                    half_leave_deductions = self.env['hr.payslip.line'].search(
                        [('id', '=', line.id), ('name', '=', "half_leave_deduction")])
                    half_leave_deduction = half_leave_deductions.amount
                vals = {
                    'employee': emp.name,
                    'desig': emp.job_title,
                    'depart': emp.department_id.name,
                    'basic': basic,
                    'absent_days': total_absent,
                    'days_working': total_days,
                    'gross': gross,
                    'tax': tax,
                    'advance_sal': adv_sal,
                    'loan': loan,
                    'mobile_bill': mobile_bill,
                    'absent_deduction': absent_deduction,
                    'late_deduction': late_deduction,
                    'short_leave_deduction': short_leave_deduction,
                    'half_leave_deduction': half_leave_deduction,
                    'net': net,
                }
                temp.append(vals)
                temp2 = temp
                data_temp.append(
                    [temp2])

        if type == 'dpt':
            department = self.env['hr.department'].search([('id', 'in', department_id)])
            for dept in department:
                employee = self.env['hr.employee'].search([('department_id', '=', dept.id)])
                for emp in employee:
                    payslip = self.env['hr.payslip'].search(
                        [('employee_id', '=', emp.id), ('month', '=', month), ('year', '=', year)])
                    total_days = 0
                    total_absent = 0
                    for slip in payslip:
                        date_start = slip.date_from
                        date_end = slip.date_to
                        date_avg = date_end - date_start
                        total_days = date_avg.days + 1

                        if emp.contract_id.date_start > date_start:
                            temp_start_date = emp.joining_date
                        else:
                            temp_start_date = date_start
                        status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                          ('status', '=', 'Absent'),
                                                                          ('out_status', '!=', 'Absent'),
                                                                          ('current_shiftatt_date', '>=', temp_start_date),
                                                                          ('current_shiftatt_date', '<=', date_end)])

                        out_status_absent = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                                              ('status', '!=', 'Absent'),
                                                                              ('out_status', '=', 'Absent'),
                                                                              ('current_shiftatt_date', '>=',
                                                                               temp_start_date),
                                                                              ('current_shiftatt_date', '<=', date_end)])
                        total_absent = len(status_absent) + len(out_status_absent)

                    payslip_line = self.env['hr.payslip.line'].search(
                        [('employee_id', '=', emp.id), ('slip_id.month', '=', month), ('slip_id.year', '=', year)])
                    temp = []
                    basic = 0
                    gross = 0
                    net = 0
                    tax = 0
                    adv_sal = 0
                    loan = 0
                    mobile_bill = 0
                    absent_deduction = 0
                    late_deduction = 0
                    short_leave_deduction = 0
                    half_leave_deduction = 0
                    for line in payslip_line:
                        basics = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Basic Salary")])
                        basic += basics.amount
                        grosses = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Gross Salary")])
                        gross += grosses.amount
                        nets = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Net Salary")])
                        net += nets.amount
                        taxs = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Tax")])
                        tax += taxs.amount
                        adv_sals = self.env['hr.payslip.line'].search(
                            [('id', '=', line.id), ('name', '=', "Advance Salary")])
                        adv_sal += adv_sals.amount
                        loans = self.env['hr.payslip.line'].search([('id', '=', line.id), ('name', '=', "Loan")])
                        loan += loans.amount
                        mobile_bills = self.env['hr.payslip.line'].search(
                            [('id', '=', line.id), ('name', '=', "Mobile Bill")])
                        mobile_bill += mobile_bills.amount
                        absent_deductions = self.env['hr.payslip.line'].search(
                            [('id', '=', line.id), ('name', '=', "Absent Deductions")])
                        absent_deduction += absent_deductions.amount
                        late_deductions = self.env['hr.payslip.line'].search(
                            [('id', '=', line.id), ('name', '=', "Late Deductions")])
                        late_deduction = late_deductions.amount
                        short_leave_deductions = self.env['hr.payslip.line'].search(
                            [('id', '=', line.id), ('name', '=', "Short Leave Deductions")])
                        short_leave_deduction += short_leave_deductions.amount
                        half_leave_deductions = self.env['hr.payslip.line'].search(
                            [('id', '=', line.id), ('name', '=', "half_leave_deduction")])
                        half_leave_deduction = half_leave_deductions.amount
                    vals = {
                        'employee': emp.name,
                        'desig': emp.job_title,
                        'depart': emp.department_id.name,
                        'basic': basic,
                        'absent_days': total_absent,
                        'days_working': total_days,
                        'gross': gross,
                        'tax': tax,
                        'advance_sal': adv_sal,
                        'loan': loan,
                        'mobile_bill': mobile_bill,
                        'absent_deduction': absent_deduction,
                        'late_deduction': late_deduction,
                        'short_leave_deduction': short_leave_deduction,
                        'half_leave_deduction': half_leave_deduction,
                        'net': net,
                    }
                    temp.append(vals)
                    temp2 = temp
                    data_temp.append(
                        [temp2])

        return {
            'doc_ids': self.ids,
            'doc_model': 'salary.summary.report.wizard',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'type': type,
            'company_id': company_id,
        }
