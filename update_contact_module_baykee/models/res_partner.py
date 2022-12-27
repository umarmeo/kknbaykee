from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    strn = fields.Char(string="STRN")

