# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from lxml import etree
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class HrAdvanceLoan(models.Model):
    _name = 'hr.advance.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Advance Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrAdvanceLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=False, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee", store=True)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    installment = fields.Integer(string="No Of Installments", default=1, help="Number of installments")
    payment_date = fields.Date(string="Payment Start Date", required=True,
                               default=fields.Date.today().replace(day=1) + relativedelta(months=1), help="Date of "
                                                                                                          "the"
                                                                                                          "paymemt")
    loan_lines = fields.One2many('hr.advance.loan.line', 'loan_id', string="Loan Line", index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount")
    adv_sal_amount = fields.Float(string="Advance Salary Amount", required=True, help="Advance Salary Amount")
    total_amount = fields.Float(string="Total Amount", store=True, readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", store=True, compute='_compute_loan_amount',
                                  help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True, compute='_compute_loan_amount',
                                     help="Total paid amount")
    month = fields.Integer(string="Month", compute='compute_month_year')
    year = fields.Integer(string="Year", compute='compute_month_year')
    advance_paid = fields.Boolean(string="Paid", help="Paid")
    current_user = fields.Many2one('res.users', 'Requested By', default=lambda self: self.env.user)
    approved_user = fields.Many2one('res.users', 'Approved By')

    type = fields.Selection([
        ('ad_sal', "Advance Salary"),
        ('loan', "Loan"),
    ], string="Type", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New') and vals.get('type') == 'loan':
            # loan_count = self.env['hr.advance.loan'].search_count(
            #     [('employee_id', '=', vals['employee_id']), ('state', '=', 'approve'), ('type', '=', 'loan'),
            #      ('balance_amount', '!=', 0)])
            # if loan_count:
            #     raise ValidationError(_("The employee has already a pending Loan installment"))
            # else:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.advance.loan.seq') or _('New')
        if vals.get('name', _('New')) == _('New') and vals.get('type') == 'ad_sal':
            # advance_count = self.env['hr.advance.loan'].search_count(
            #     [('employee_id', '=', vals['employee_id']), ('state', '=', 'approve'), ('type', '=', 'ad_sal'),
            #      ('advance_paid', '!=', True)])
            # if advance_count:
            #     raise ValidationError(_("The employee has already taken Advance"))
            # else:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.advance.salary.seq') or _('New')
        res = super(HrAdvanceLoan, self).create(vals)
        return res

    @api.depends('payment_date')
    def compute_month_year(self):
        for rec in self:
            if rec.payment_date:
                rec.year = rec.payment_date.year
                rec.month = rec.payment_date.month

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.advance.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def reset_to_draft(self):
        return self.write({'state': 'draft'})

    def action_submit(self):
        search_contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        print(search_contract)
        if search_contract:
            self.write({'state': 'waiting_approval_1'})
        else:
            raise UserError(_('No Contract Found for this Employee'))

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            if not data.loan_lines and data.type == 'loan':
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve', 'approved_user': self.env.user.id})

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'refuse'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrAdvanceLoan, self).unlink()

    def _get_report_loan_advance_base_filename(self):
        return self._get_loan_advances_display_name()

    def _get_loan_advances_display_name(self, show_ref=False):
        self.ensure_one()
        name = ''
        name += {
            'loan': _('Loan Application Form'),
            'ad_sal': _('Advance Salary Application Form'),
        }[self.type]
        name += ' '
        return name


class InstallmentLine(models.Model):
    _name = "hr.advance.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    month = fields.Integer(string="Month", compute='compute_month_year')
    year = fields.Integer(string="Year", compute='compute_month_year')
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('hr.advance.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")

    @api.depends('date')
    def compute_month_year(self):
        for rec in self:
            if rec.date:
                rec.year = rec.date.year
                rec.month = rec.date.month


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.advance.loan'].search_count(
            [('employee_id', '=', self.id), ('type', '=', 'loan')])

    def _compute_employee_advance(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.advance_count = self.env['hr.advance.loan'].search_count(
            [('employee_id', '=', self.id), ('type', '=', 'ad_sal')])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
    advance_count = fields.Integer(string="Loan Count", compute='_compute_employee_advance')
