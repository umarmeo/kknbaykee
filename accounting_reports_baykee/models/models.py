from odoo import api, fields, models
from datetime import datetime


class InvoiceOrder(models.Model):

    _inherit = 'account.move'

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')