import datetime

from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    Basic_salary = fields.Monetary(string='Basic Salary', store=True, tracking=True)
    Allowance_fuel = fields.Monetary(string='Fuel Allowance', tracking=True)
    medical_allowance = fields.Monetary(string='Medical Allowance', store=True, tracking=True)
    Allowance_house = fields.Monetary('Allowance House', store=True, default=0.0,
                                      tracking=True)
    gross_finals = fields.Monetary('Gross', default=0.0, tracking=True)
    Deduction_Tax = fields.Monetary('Tax', default=0.0, tracking=True, compute='_tax_slabs')
    Deduction_EOBI = fields.Selection([
        ('yes', "Yes"),
        ('no', "No"),
    ], string='EOBI', default='no', tracking=True)
    Deduction_PF = fields.Selection([
        ('yes', "Yes"),
        ('no', "No"),
    ], string='PF', default='no', tracking=True)
    Deduction_Advance = fields.Monetary(string='Advance', default=0.0, tracking=True, compute='compute_advance_amount')
    Deduction_MobileBills = fields.Monetary(string='Mobile Bill', default=0.0, tracking=True)
    deduction_late = fields.Monetary(string='Late Deductions', default=0.0, tracking=True)
    deduction_absent = fields.Monetary(string='Absent Deductions', default=0.0, tracking=True)
    deduction_short_leave = fields.Monetary(string='Short Leave Deductions', default=0.0, tracking=True)
    deduction_half_leave = fields.Monetary(string='Half Leave Deductions', default=0.0, tracking=True)
    gazette_comp = fields.Monetary(string='Gazette Holiday Compensation', default=0.0, tracking=True)
    special_allowance = fields.Monetary(string='Special Allowance', default=0.0, tracking=True)
    travel_allowance = fields.Monetary(string='Travelling Allowance', default=0.0, tracking=True)
    Net_finals = fields.Monetary(string='Net Salary', store=False, default=0.0, tracking=True,
                                 compute='calculate_net_salary')
    deduction_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Attendance Deduction', default='Yes',
                                       tracking=True)
    history_contract_salary = fields.One2many('hr.contract.history', 'contract_id', string='Salary History')
    Deduction_Loan = fields.Monetary(string='Loan', tracking=True, compute='compute_loan_amount')

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='draft')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def onchange_running(self):
        self.state = 'open'

    def onchange_reset(self):
        self.state = 'draft'

    @api.onchange('Basic_salary', 'Allowance_fuel', 'medical_allowance', 'Allowance_house', 'special_allowance',
                  'gazette_comp', 'travel_allowance')
    def calculate_gross_salary(self):
        self.gross_finals = self.Basic_salary + self.Allowance_fuel + self.special_allowance + self.Allowance_house \
                            + self.medical_allowance + self.gazette_comp + self.travel_allowance
        self.wage = self.gross_finals

    # @api.depends('gross_finals')
    # def calculate_medical_allowance(self):
    #     self.medical_allowance = (self.gross_finals * 10) / 100

    @api.depends('Deduction_Tax', 'Deduction_Advance', 'Deduction_Loan', 'Deduction_MobileBills',
                 'deduction_late', 'deduction_half_leave', 'deduction_short_leave', 'gross_finals')
    def calculate_net_salary(self):
        for rec in self:
            rec.Net_finals = rec.gross_finals - rec.Deduction_Tax - rec.Deduction_Advance \
                             - rec.Deduction_Loan - rec.Deduction_MobileBills - rec.deduction_late \
                             - rec.deduction_half_leave - rec.deduction_short_leave - rec.deduction_absent

    @api.depends('gross_finals', 'date_start', 'medical_allowance')
    def _tax_slabs(self):
        for rec in self:
            rec.Deduction_Tax = 0
            yearly_wage = 12 * rec.gross_finals
            salary = rec.gross_finals
            if yearly_wage > 600000:
                print('nice')
                if 600000 < yearly_wage <= 1200000:
                    print("Please enter")
                    rec.Deduction_Tax = (salary - 50000) * 0.025
                elif 1200000 < yearly_wage <= 2400000:
                    cal_per = (((yearly_wage - 1200000) * 0.125) + 15000)
                    rec.Deduction_Tax = cal_per / 12
                elif 2400000 < yearly_wage <= 3600000:
                    cal_per = (((yearly_wage - 2400000) * 0.2) + 165000)
                    rec.Deduction_Tax = cal_per / 12
                elif 3600000 < yearly_wage <= 6000000:
                    cal_per = (((yearly_wage - 3600000) * 0.25) + 405000)
                    rec.Deduction_Tax = cal_per / 12
                elif 6000000 < yearly_wage <= 12000000:
                    cal_per = (((yearly_wage - 6000000) * 0.325) + 1005000)
                    rec.Deduction_Tax = cal_per / 12
                elif 12000000 < yearly_wage:
                    cal_per = (((yearly_wage - 12000000) * 0.35) + 2955000)
                    rec.Deduction_Tax = cal_per / 12
                else:
                    rec.Deduction_Tax = 0

    def compute_loan_amount(self):
        for rec in self:
            today_date = date.today()
            previous_date = today_date.replace(day=1) - relativedelta(months=1)
            advance_loan_lines = self.env['hr.advance.loan.line'].search(
                [('loan_id.state', '=', 'approve'), ('loan_id.employee_id', '=', rec.employee_id.id),
                 ('loan_id.type', '=', 'loan')]).filtered(
                lambda m: m.month == previous_date.month and m.year == previous_date.year)
            if advance_loan_lines:
                amount = 0
                for l in advance_loan_lines:
                    amount += l.amount
                rec.Deduction_Loan = amount
            else:
                rec.Deduction_Loan = 0

    def compute_advance_amount(self):
        for rec in self:
            today_date = date.today()
            previous_date = today_date.replace(day=1) - relativedelta(months=1)
            advance_loan = self.env['hr.advance.loan'].search(
                [('state', '=', 'approve'), ('employee_id', '=', rec.employee_id.id),
                 ('type', '=', 'ad_sal')]).filtered(
                lambda m: m.month == previous_date.month and m.year == previous_date.year)
            if advance_loan:
                amount = 0
                for l in advance_loan:
                    amount += l.adv_sal_amount
                rec.Deduction_Advance = amount
            else:
                rec.Deduction_Advance = 0
