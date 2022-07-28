# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class update_account_module_baykee(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('check', 'To Check'),
        ('coo approval', 'COO Approval'),
        ('ceo approval', 'CEO Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    checked_uid = fields.Many2one('res.users', 'Checked By', tracking=True)
    checked_date = fields.Datetime('Checked Date', tracking=True)

    coo_uid = fields.Many2one('res.users', 'COO By', tracking=True)
    coo_date = fields.Datetime('COO Approved Date', tracking=True)

    ceo_uid = fields.Many2one('res.users', 'CEO By', tracking=True)
    ceo_date = fields.Datetime('CEO Approved Date', tracking=True)

    post_uid = fields.Many2one('res.users', 'Post By', tracking=True)
    post_date = fields.Datetime('POST Date', tracking=True)

    def submit_for_check(self):
        self.state = 'check'

    def submit_for_coo_approval(self):
        if self.journal_id:
            if self.journal_id.type in ('bank', 'cash'):
                self.state = 'coo approval'
            else:
                self.action_post()
        else:
            raise ValidationError('Select Journal')
        self.checked_uid = self.env.user
        self.checked_date = datetime.datetime.now()

    def reset_to_draft_from_check(self):
        self.state = 'draft'

    def submit_for_ceo_approval(self):
        self.state = 'ceo approval'
        self.coo_uid = self.env.user
        self.coo_date = datetime.datetime.now()

    def coo_reject(self):
        self.state = 'rejected'

    def coo_sent_in_check(self):
        self.state = 'check'

    def button_approved(self):
        self.state = 'approved'
        self.ceo_uid = self.env.user
        self.ceo_date = datetime.datetime.now()

    def ceo_reject(self):
        self.state = 'rejected'
        # self.show_reset_to_draft_button = True

    def ceo_sent_to_coo(self):
        self.state = 'ceo approval'

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in ('posted', 'cancel', 'rejected')

    def action_post(self):
        self.post_date = datetime.datetime.now()
        self.post_uid = self.env.user
        if self.payment_id:
            self.payment_id.action_post()
        else:
            self._post(soft=False)
        return False