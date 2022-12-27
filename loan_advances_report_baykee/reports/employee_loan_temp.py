from odoo import api, fields, models
import datetime


class EmployeeLoanReportTemplate(models.AbstractModel):
    _name = 'report.loan_advances_report_baykee.loan_employee_report'
    _description = 'Loan To Employees Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['loan.employee.wizard'].browse(docids[0])
        company_id = self.env.user.company_id
        month = docs.month
        year = docs.year
        loan = self.env['hr.advance.loan'].search(
            [('type', '=', 'loan'), ('state', '=', 'approve')])
        for lo in loan:
            loan_lines = lo.loan_lines.filtered(lambda ln: ln.month == int(month) and ln.year == int(year))
            for line in loan_lines:
                temp = []
                vals = {
                    'employee': lo.employee_id.name,
                    'desig': lo.employee_id.job_title,
                    'depart': lo.employee_id.department_id.name,
                    'amount': lo.loan_amount,
                    'payment_date': line.date,
                    'installment': line.amount,
                    'balance': lo.balance_amount,
                }
                temp.append(vals)
                temp2 = temp
                data_temp.append(
                    [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'advance.against.salary.wizard',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'company_id': company_id,
        }
