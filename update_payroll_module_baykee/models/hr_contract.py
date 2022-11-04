# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    advance_loan_date = fields.Date(string="Advance Loan Date")
    # next_advance_loan_date = fields.Date(string="Next Advance Loan Date")
    advance_loan_amount = fields.Float(string="Advance Loan Amount")

    def compute_advance_loan_date_and_amount(self):
        for rec in self:
            today_date = date.today()
            previous_date = today_date - relativedelta(months=1)
            advance_loan_lines = self.env['hr.advance.loan.line'].search(
                [('loan_id.employee_id', '=', rec.employee_id.id), ('date', '<', previous_date)])
            print(advance_loan_lines)
            if advance_loan_lines:
                for l in advance_loan_lines:
                    rec.advance_loan_date = l.date
                    rec.advance_loan_amount = l.amount
            else:
                rec.advance_loan_date = False
                rec.advance_loan_amount = False
