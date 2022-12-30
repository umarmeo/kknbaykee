import time
import math
import datetime
from datetime import datetime
import calendar
import logging
import calendar
from odoo.exceptions import UserError
import pdb
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import logging


class PartyWisePurchaseReport(models.TransientModel):
    _name = 'party.wise.purchase.report'
    _description = "Party Wise Purchase Report"

    start_date = fields.Date(string="Start Date", default=datetime.today().replace(day=1))

    @api.model
    def _default_end_date(self):
        first = datetime.today().replace(day=1)
        last = first + relativedelta(months=1) + timedelta(days=-1)
        return last

    end_date = fields.Date(string="End Date", default=_default_end_date)
    product_id = fields.Many2many('product.product', string="Products")
    analytic_account_id = fields.Many2many('account.analytic.account', string="Analytic Account")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string="Analytic Tags")

