import datetime
from datetime import datetime
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class PendingBillsReport(models.TransientModel):
    _name = 'pending.bills.report'
    _description = "Pending Bills Report"

    start_date = fields.Date(string="Start Date", default=datetime.today().replace(day=1))

    @api.model
    def _default_end_date(self):
        first = datetime.today().replace(day=1)
        last = first + relativedelta(months=1) + timedelta(days=-1)
        return last

    end_date = fields.Date(string="End Date", default=_default_end_date)


