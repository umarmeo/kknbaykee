# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api


class update_sale_module_baykee(models.Model):
    _inherit = 'sale.order'

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale'
        }