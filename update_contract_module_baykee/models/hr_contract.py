import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    incremented_date = fields.Datetime(string="Increment Date", tracking=True)
    Basic_salary = fields.Monetary(string='Basic Salary', store=True, tracking=True)
    Allowance_fuel = fields.Monetary(string='Fuel Allowance', tracking=True)
    medical_allowance = fields.Monetary(string='Medical Allowance', store=True, tracking=True)
    total_salary = fields.Monetary('Total Salary', tracking=True)
    Allowance_house = fields.Monetary('Allowance House', store=True, default=0.0,
                                      tracking=True)
    gross_finals = fields.Monetary('Gross', default=0.0, tracking=True)
    Deduction_Tax = fields.Monetary('Tax', default=0.0, tracking=True, compute='_tax_slabs')
    Deduction_EOBI = fields.Monetary('EOBI', default=0.0, tracking=True)
    Deduction_PF = fields.Monetary('PF', default=0.0, tracking=True)
    Deduction_Advance = fields.Monetary('Advance', default=0.0, tracking=True)
    Deduction_MobileBills = fields.Monetary('Mobile Bill', default=0.0, tracking=True)
    deduction_lates = fields.Monetary('Late Deductions', default=0.0, tracking=True)
    deduction_absent = fields.Monetary('Absent Deductions', default=0.0, tracking=True)
    gazette_comp = fields.Monetary('Gazette Holiday Compensation', default=0.0, tracking=True)
    special_allowance = fields.Monetary('Special Allowance', default=0.0, tracking=True)
    Deduction_Finals = fields.Monetary('Deduction Finals', default=0.0, store=False,
                                       tracking=True)
    Net_finals = fields.Monetary('Net', store=False, default=0.0, tracking=True)
    deduction_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Attendance Deduction', default='Yes',
                                       tracking=True)
    history_contract_salary = fields.One2many('hr.contract.history', 'contract_id', string='Salary History')
    arrears = fields.Monetary('Arrears', tracking=True)
    Deduction_Loan = fields.Monetary('Loan', tracking=True)

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

    @api.depends('wage', 'date_start')
    def _tax_slabs(self):
        for rec in self:
            yearly_wage = 12 * rec.wage
            salary = rec.wage
            if yearly_wage > 600000:
                if 600000 < yearly_wage <= 1200000:
                    rec.Deduction_Tax = (salary - 50000) * 0.025
                elif 1200000 < yearly_wage <= 2400000:
                    rec.Deduction_Tax = (((salary - 100000) * 0.125) + 15000)
                elif 2400000 < salary <= 3600000:
                    rec.Deduction_Tax = (((salary - 150000) * 0.2) + 165000)
                elif 3600000 < salary <= 6000000:
                    rec.Deduction_Tax = (((salary - 208333.33) * 0.25) + 405000)
                elif 6000000 < salary <= 12000000:
                    rec.Deduction_Tax = (((salary - 291666.66) * 0.325) + 1005000)
                # elif 416666.66 < salary <= 666666.66:
                #     rec.Deduction_Tax = (((salary - 416666.66) * 0.225) + 55833.33)
                # elif 666666.66 < salary <= 1000000:
                #     rec.Deduction_Tax = (((salary - 666666.66) * 0.25) + 112083.33)
                # elif 1000000 < salary <= 2500000:
                #     rec.Deduction_Tax = (((salary - 1000000) * 0.275) + 195416.66)
                # elif 2500000 < salary <= 4166666.66:
                #     rec.Deduction_Tax = (((salary - 2500000) * 0.3) + 607916.66)
                # elif 4166666.66 < salary <= 6250000:
                #     rec.Deduction_Tax = (((salary - 4166666.66) * 0.325) + 1107916.66)
                # elif salary > 6250000:
                #     rec.Deduction_Tax = (((salary - 6250000) * 0.35) + 1785000)
                else:
                    rec.Deduction_Tax = 0
            else:
                rec.Deduction_Tax = 0

# class HrContractHistory(models.Model):
#     _inherit = 'hr.contract.history'
#
#     contract_id = fields.Many2one('hr.contract', string="Contract")
#     user_id = fields.Many2one('res.users', string="User")
#     Basic_salary = fields.Monetary(string='Basic Salary', default=0.0, tracking=True)
#     Allowance_fuel = fields.Monetary(string='Allowance Fuel', default=0.0, tracking=True)
#     Allowance_house = fields.Monetary(string='Allowance House', default=0.0, tracking=True)
#     gross_finals = fields.Monetary(string='Gross', default=0.0, tracking=True)
#     in_date = fields.Datetime(string="In Date")
#     incremented_date = fields.Datetime(string="Increment Date")
#     currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
#                                   default=lambda self: self.env.company.currency_id)
