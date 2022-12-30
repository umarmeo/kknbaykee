from odoo import api, fields, models
import datetime


class AdvanceAgainstSalaryReportTemplate(models.AbstractModel):
    _name = 'report.loan_advances_report_baykee.advance_salary_report'
    _description = 'Advance Against Salary Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['advance.against.salary.wizard'].browse(docids[0])
        company_id = self.env.user.company_id
        month = docs.month
        year = docs.year
        domain = [('type', '=', 'ad_sal'), ('state', '=', 'approve')]
        if docs.department_id:
            domain += [('department_id', '=', docs.department_id.id)]
        advance_salary = self.env['hr.advance.loan'].search(domain).filtered(
            lambda ln: ln.month == int(month) and ln.year == int(year))
        for ad_sal in advance_salary:
            temp = []
            vals = {
                'employee': ad_sal.employee_id.name,
                'desig': ad_sal.employee_id.job_title,
                'depart': ad_sal.department_id.name,
                'payment_date': ad_sal.payment_date,
                'amount': ad_sal.adv_sal_amount,
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
