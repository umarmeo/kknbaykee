import datetime
from datetime import datetime
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)
import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class SalePersonWiseSaleReport(models.TransientModel):
    _name = 'sale.person.wise.sale.report'
    _description = "Sale Person Wise Sale Report"

    start_date = fields.Date(string="Start Date", default=datetime.today().replace(day=1))

    @api.model
    def _default_end_date(self):
        first = datetime.today().replace(day=1)
        last = first + relativedelta(months=1) + timedelta(days=-1)
        return last

    end_date = fields.Date(string="End Date", default=_default_end_date)
    sale_person = fields.Many2many('res.users', string="Sale Person")
    analytic_account_id = fields.Many2many('account.analytic.account', string="Analytic Account")
    analytic_tag_id = fields.Many2many('account.analytic.tag', string="Analytic Tags")
