# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # advance_loan_date = fields.Date(string="Advance Loan Date")
    # next_advance_loan_date = fields.Date(string="Next Advance Loan Date")
    # advance_loan_amount = fields.Float(string="Advance Loan Amount", compute="compute_advance_loan_date_and_amount")

    def compute_advance_loan_date_and_amount(self):
        for rec in self:
            rec.advance_loan_amount = 0
            today_date = date.today()
            previous_date = today_date.replace(day=1) - relativedelta(months=1)
            advance_loan_lines = self.env['hr.advance.loan.line'].search(
                [('loan_id.employee_id', '=', rec.employee_id.id), ('date', '=', previous_date), ('date', '=', previous_date)])
            if advance_loan_lines:
                for l in advance_loan_lines:
                    rec.advance_loan_amount = l.amount
                    rec.Deduction_Loan = l.amount
