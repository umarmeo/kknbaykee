# -*- coding: utf-8 -*-

from odoo import models, fields, api

class payment_process_division(models.Model):
    _name = 'payment.division'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This Model create For Division.'

    name = fields.Char('Name', tracking=True, required=True)