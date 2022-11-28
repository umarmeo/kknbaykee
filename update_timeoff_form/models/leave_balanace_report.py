import datetime
import logging
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class HRLeaveBalanceReport(models.TransientModel):
    _name = 'hr.leave.balance.report'
    _description = 'HR Leave Balance Report'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    employee_id = fields.Many2one('hr.employee', 'Employee', domain="[('company_id', '=', company_id)]")

    start_date = fields.Date('Start Date', required=True, default=datetime.date(day=1, month=1, year=2021))
    end_date = fields.Date('End Date', required=True, default=datetime.date.today())
