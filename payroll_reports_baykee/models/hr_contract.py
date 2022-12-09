from odoo import models, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    Deduction_EOBI_amount = fields.Monetary(string="EOBI Amount", default=0.0, tracking=True)
    Deduction_PF_amount = fields.Monetary(string="PF Amount", default=0.0, tracking=True)