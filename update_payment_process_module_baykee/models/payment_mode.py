# -*- coding: utf-8 -*-

from odoo import models, fields, api

class payment_mode(models.Model):
    _name = 'payment.mode'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This Model create For Payment Mode.'

    name = fields.Char('Name', tracking=True, required=True)