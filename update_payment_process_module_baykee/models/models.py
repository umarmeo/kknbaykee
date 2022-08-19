# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class update_payment_process(models.Model):
    _name = 'payment.process'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This class can contain 2 fields and states for amount.'

    name = fields.Char(string='Name', readonly=True,
                       index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')

    amount = fields.Monetary('Amount', tracking=True, required=True)
    purpose = fields.Text('Purpose', tracking=True, required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('manager', 'Manager Approval'),
        ('coo', 'COO Approval'),
        ('ceo', 'CEO Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ('reject', 'Reject'),
    ], string='Status', tracking=True,
        default='draft')
    manager_uid = fields.Many2one('res.users', string='Manager uid', tracking=True)
    manager_date_time = fields.Datetime('Manager Date and Time', tracking=True)
    coo_uid = fields.Many2one('res.users', string='COO uid', tracking=True)
    coo_date_time = fields.Datetime('COO Date and Time', tracking=True)
    ceo_uid = fields.Many2one('res.users', string='CEO uid', tracking=True)
    ceo_date_time = fields.Datetime('CEO Date and Time', tracking=True)
    submit_uid = fields.Many2one('res.users', string='Submit uid', tracking=True)
    submit_date_time = fields.Datetime('Submit Date and Time', tracking=True)
    division = fields.Many2one('payment.division', string="Division", tracking=True, required=False)
    term = fields.Selection(selection=[
        ('advance', 'Advance'),
        ('reimbursement', 'Reimbursement'),
    ], string='Term', tracking=True, default='advance',required=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', tracking=True, required=False)
    payment_mode = fields.Many2one('payment.mode', string="Payment Mode", tracking=True, required=False)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.process') or _('New')
        number = super(update_payment_process, self).create(vals)
        return number

    def action_manager_approval(self):
        self.submit_uid = self.env.user.id
        self.submit_date_time = datetime.now()
        if self.amount <= 0:
            raise ValidationError('Cannot move to next state because amount is zero')
        else:
            self.state = 'manager'

    def action_coo_approval(self):
        self.manager_uid = self.env.user.id
        self.manager_date_time = datetime.now()
        self.state = 'coo'

    def action_ceo_approval(self):
        self.coo_uid = self.env.user.id
        self.coo_date_time = datetime.now()
        self.state = 'ceo'

    def action_approved(self):
        self.ceo_uid = self.env.user.id
        self.ceo_date_time = datetime.now()
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset_to_draft(self):
        self.state = 'draft'

    def action_reset_to_manager(self):
        self.state = 'manager'

    def action_reset_to_coo(self):
        self.state = 'coo'

    def action_reject(self):
        self.state = 'reject'
