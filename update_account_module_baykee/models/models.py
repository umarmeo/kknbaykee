# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from collections import defaultdict


class update_account_module_baykee(models.Model):
    _inherit = 'account.move'

    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        move_type = self._context.get('default_move_type', 'entry')
        if move_type in self.get_sale_types(include_receipts=True):
            journal_types = ['sale']
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_types = ['purchase']
        else:
            journal_types = self._context.get('default_move_journal_types', ['general'])

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type not in journal_types:
                raise UserError(_(
                    "Cannot create an invoice of type %(move_type)s with a journal having %(journal_type)s as type.",
                    move_type=move_type,
                    journal_type=journal.type,
                ))
        else:
            journal = self._search_default_journal(journal_types)

        return journal

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 check_company=True, domain="",
                                 default=_get_default_journal)

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

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        def journal_key(move):
            return (move.journal_id, move.journal_id.refund_sequence and move.move_type)

        def date_key(move):
            return (move.date.year, move.date.month)

        grouped = defaultdict(  # key: journal_id, move_type
            lambda: defaultdict(  # key: first adjacent (date.year, date.month)
                lambda: {
                    'records': self.env['account.move'],
                    'format': False,
                    'format_values': False,
                    'reset': False
                }
            )
        )
        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))
        highest_name = self[0]._get_last_sequence(lock=False) if self else False

        # Group the moves by journal and month
        for move in self:
            if not highest_name and move == self[0] and not move.state == 'check' and move.date:
                # In the form view, we need to compute a default sequence so that the user can edit
                # it. We only check the first move as an approximation (enough for new in form view)
                pass
            elif (move.name and move.name != '/') or move.state != 'check':
                try:
                    if not move.state == 'check':
                        move._constrains_date_sequence()
                    # Has already a name or is not posted, we don't add to a batch
                    continue
                except ValidationError:
                    # Has never been posted and the name doesn't match the date: recompute it
                    pass
            group = grouped[journal_key(move)][date_key(move)]
            if not group['records']:
                # Compute all the values needed to sequence this whole group
                move._set_next_sequence()
                group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
                group['reset'] = move._deduce_sequence_number_reset(move.name)
            group['records'] += move

        # Fusion the groups depending on the sequence reset and the format used because `seq` is
        # the same counter for multiple groups that might be spread in multiple months.
        final_batches = []
        for journal_group in grouped.values():
            journal_group_changed = True
            for date_group in journal_group.values():
                if (
                        journal_group_changed
                        or final_batches[-1]['format'] != date_group['format']
                        or dict(final_batches[-1]['format_values'], seq=0) != dict(date_group['format_values'], seq=0)
                ):
                    final_batches += [date_group]
                    journal_group_changed = False
                elif date_group['reset'] == 'never':
                    final_batches[-1]['records'] += date_group['records']
                elif (
                        date_group['reset'] == 'year'
                        and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
                ):
                    final_batches[-1]['records'] += date_group['records']
                else:
                    final_batches += [date_group]

        # Give the name based on previously computed values
        for batch in final_batches:
            for move in batch['records']:
                move.name = batch['format'].format(**batch['format_values'])
                batch['format_values']['seq'] += 1
            batch['records']._compute_split_sequence()

        self.filtered(lambda m: not m.name).name = '/'

    def submit_for_check(self):
        self.state = 'check'

    def submit_for_coo_approval(self):
        if self.journal_id:
            if self.journal_id.code in ('CPV', 'BPV', 'CRV', 'BRV'):
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
        self._get_last_sequence(lock=False)
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
            move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in (
                'posted', 'cancel', 'rejected')

    def action_post(self):
        self.post_date = datetime.datetime.now()
        self.post_uid = self.env.user
        if self.payment_id:
            self.payment_id.action_post()
        else:
            self._post(soft=False)
        return False
