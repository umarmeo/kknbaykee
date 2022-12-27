import datetime
from datetime import datetime
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class PendingBillsReport(models.TransientModel):
    _name = 'pending.bills.report'
    _description = "Pending Bills Report"

    start_date = fields.Date(string="Start Date", default=datetime.today().replace(day=1))
    report_type = fields.Selection([
        ('division_wise', "Division Wise"),
        ('project_wise', "Project Wise"),
    ], string="Report Type")
    analytic_account_id = fields.Many2many('account.analytic.account', string="Analytic Account")
    analytic_tag_id = fields.Many2many('account.analytic.tag', string="Analytic Tag")

    @api.model
    def _default_end_date(self):
        first = datetime.today().replace(day=1)
        last = first + relativedelta(months=1) + timedelta(days=-1)
        return last

    end_date = fields.Date(string="End Date", default=_default_end_date)


