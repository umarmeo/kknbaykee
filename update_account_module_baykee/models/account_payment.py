# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class update_account_module_baykee(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

        self.filtered(
            lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
        )._create_paired_internal_transfer_payment()
