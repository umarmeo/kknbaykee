import datetime
from datetime import datetime
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class AgeReceivableReport(models.TransientModel):
    _name = 'age.receivable.report'
    _description = "Age Receivable Report"

    date = fields.Date(string="Date", default=datetime.today())
    partner_id = fields.Many2many('res.partner', string="Partners")
    analytic_account_id = fields.Many2many('account.analytic.account', string="Analytic Account")
    analytic_tag_id = fields.Many2many('account.analytic.tag', string="Analytic Tags")
