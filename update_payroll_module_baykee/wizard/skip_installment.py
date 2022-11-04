from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class LoanSkipInstallment(models.TransientModel):
    _name = 'loan.skip.installment'

    @api.model
    def _get_installment_lines(self):
        # if self.env.context.get('active_model', False) == 'hr.advance.loan.line' and self.env.context.get(
        #         'active_ids', False):
        active_ids = (self.env.context['active_ids'])
        payment_lines = self.env['hr.advance.loan.line'].search([('loan_id', '=', active_ids)])
        return payment_lines

    payment_date = fields.Date(string="Payment Date")
    installment_lines = fields.Many2many('hr.advance.loan.line', string="Installments Lines",
                                         default=_get_installment_lines)

    def skip_installment(self):
        active_ids = (self.env.context['active_ids'])
        advance_loan = self.env['hr.advance.loan'].search([('id', '=', active_ids)])
        installment_lines = self.env['hr.advance.loan.line'].search(
            [('loan_id', '=', active_ids), ('date', '=', self.payment_date)])
        print(installment_lines)
        if not installment_lines:
            raise ValidationError(_("Date doesn't exist"))
        installment_lines.with_context(_force_unlink=True).unlink()
        installment_lines_new = self.env['hr.advance.loan.line'].search(
            [('loan_id', '=', active_ids)], order='id desc', limit=1)
        date_new = installment_lines_new.date + relativedelta(months=+1)
        print(date_new)
        val = {
            'date': date_new,
            'amount': installment_lines.amount,
            'loan_id': advance_loan.id,
            'employee_id': advance_loan.employee_id.id
        }
        advance_loan.loan_lines.create(val)


