from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import format_date


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def create_payroll_for_previous_month_manual(self):
        for rec in self:
            existing_payroll = self.search([
                ('date_start', '=', rec.date_start),
                ('date_end', '=', rec.date_end),
                ('id', '!=', rec.ids),
            ])
            print(existing_payroll)
            if len(existing_payroll) > 0:
                raise ValidationError('Payroll already generated.')
            employees = self.env['hr.employee'].search([('active', '=', True)])

            start_date = rec.date_start
            end_date = rec.date_end

            employee_ids = []
            for employee in employees:
                employee_ids.append((4, employee.id))
                rec.update_contract_payroll(employee, start_date, end_date)
            query = "delete from hr_work_entry;"
            self.env.cr.execute(query)
            vals = {
                "name": "Payroll " + start_date.strftime("%b") + ' ' + str(start_date.year),
                "company_id": self.env.company.id
            }
            rec.write(vals)
            # I create a payslip employee.
            search_structure = self.env['hr.payroll.structure'].search([('current_structure', '=', True)], limit=1)
        
            payslip_employee = self.env['hr.payslip.employees'].create({
                'employee_ids': employee_ids,
                'structure_id': search_structure.id,
            })

            # I generate the payslip by clicking on Generate button wizard.
            payslip_employee.with_context(active_id=rec.ids[0]).compute_sheet()

    def update_contract_payroll(self, employee, start_date, end_date):
        total_days = end_date - start_date
        total_days = total_days.days + 1
        contract = self.env['hr.contract'].search([('employee_id', '=', employee.id),
                                                   ('state', '=', 'open')], limit=1)
        if len(contract) == 1:
            contract.deduction_late = 0
            contract.deduction_half_leave = 0
            contract.deduction_short_leave = 0
            if contract.deduction_check == 'Yes':
                if employee.contract_id.date_start > start_date:
                    temp_start_date = employee.joining_date
                else:
                    temp_start_date = start_date

                both_absent = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                ('status', '=', 'Absent'),
                                                                ('out_status', '=', 'Absent'),
                                                                ('current_shiftatt_date', '>=', temp_start_date),
                                                                ('current_shiftatt_date', '<=', end_date)])

                status_absent = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                  ('status', '=', 'Absent'),
                                                                  ('out_status', '!=', 'Absent'),
                                                                  ('current_shiftatt_date', '>=', temp_start_date),
                                                                  ('current_shiftatt_date', '<=', end_date)])

                out_status_absent = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                      ('status', '!=', 'Absent'),
                                                                      ('out_status', '=', 'Absent'),
                                                                      ('current_shiftatt_date', '>=', temp_start_date),
                                                                      ('current_shiftatt_date', '<=', end_date)])
                total_absent = len(both_absent) + len(status_absent) + len(out_status_absent)
                if total_absent > 0:
                    contract.deduction_absent = (contract.gross_finals / total_days) * total_absent

                # both_late = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                #                                               ('status', '=', 'Late'),
                #                                               ('out_status', '=', 'Late'),
                #                                               ('current_shiftatt_date', '>=', temp_start_date),
                #                                               ('current_shiftatt_date', '<=', end_date)])

                status_late = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                ('status', '=', 'Late'),
                                                                ('out_status', 'not in', ('Absent', 'Late')),
                                                                ('current_shiftatt_date', '>=', temp_start_date),
                                                                ('current_shiftatt_date', '<=', end_date)])

                out_status_late = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                    ('status', 'not in', ('Absent', 'Late')),
                                                                    ('out_status', '=', 'Late'),
                                                                    ('current_shiftatt_date', '>=', temp_start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])

                total_late = len(status_late) + len(out_status_late)
                if total_late >= 4:
                    total_late_process = total_late / 4
                    contract.deduction_late = (contract.gross_finals / total_days) * int(total_late_process)

                # both_short = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                #                                                ('status', '=', 'ShortLeave'),
                #                                                ('out_status', '=', 'ShortLeave'),
                #                                                ('current_shiftatt_date', '>=', temp_start_date),
                #                                                ('current_shiftatt_date', '<=', end_date)])
                # print(both_short)

                status_short = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                 ('status', '=', 'ShortLeave'),
                                                                 ('out_status', 'not in', ('Absent', 'ShortLeave')),
                                                                 ('current_shiftatt_date', '>=', temp_start_date),
                                                                 ('current_shiftatt_date', '<=', end_date)])

                out_status_short = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                     ('status', 'not in', ('Absent', 'ShortLeave')),
                                                                     ('out_status', '=', 'ShortLeave'),
                                                                     ('current_shiftatt_date', '>=', temp_start_date),
                                                                     ('current_shiftatt_date', '<=', end_date)])
                total_short_leaves = len(status_short) + len(out_status_short)
                total_short_leaves_proces = total_short_leaves * 0.334
                contract.deduction_short_leave = (contract.gross_finals / total_days) * total_short_leaves_proces

                status_half = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                ('status', '=', 'HalfLeave'),
                                                                ('current_shiftatt_date', '>=', temp_start_date),
                                                                ('current_shiftatt_date', '<=', end_date)])

                out_status_half = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                    ('out_status', '=', 'HalfLeave'),
                                                                    ('current_shiftatt_date', '>=', temp_start_date),
                                                                    ('current_shiftatt_date', '<=', end_date)])
                total_half_leaves = len(status_half) + len(out_status_half)
                total_half_leaves_proces = total_half_leaves * 0.5
                contract.deduction_half_leave = (contract.gross_finals / total_days) * total_half_leaves_proces

    def rerun_payroll_for_previous_month_manual(self):
        start_date = self.date_start
        end_date = self.date_end
        employees = self.env['hr.employee'].search([('active', '=', True)])
        for employee in employees:
            self.update_contract_payroll(employee, start_date, end_date)
        payslips = self.env['hr.payslip'].search([('payslip_run_id', '=', self.id), ('state', '!=', 'cancel')])
        payslips.compute_sheet()


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    current_structure = fields.Boolean(string="Current Structure")

