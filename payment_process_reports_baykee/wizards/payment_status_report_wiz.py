from odoo import fields, models, api
import datetime


class PaymentStatusReportWizard(models.TransientModel):
    _name = 'payment.status.wiz'
    _description = 'Payment Status Report Wizard'

    # month = fields.Selection([
    #     ('1', "January"),
    #     ('2', "February"),
    #     ('3', "March"),
    #     ('4', "April"),
    #     ('5', "May"),
    #     ('6', "June"),
    #     ('7', "July"),
    #     ('8', "August"),
    #     ('9', "September"),
    #     ('10', "October"),
    #     ('11', "November"),
    #     ('12', "December"),
    # ], string="Month")
    #
    # @api.model
    # def year_selection(self):
    #     year = 2000
    #     year_list = []
    #     while year != 2090:
    #         year_list.append((str(year), str(year)))
    #         year += 1
    #     return year_list

    # year = fields.Selection(year_selection, string="Year", default=datetime.date.today().year)
    division_id = fields.Many2many('payment.division', string="Division")
    analytic_account_id = fields.Many2many('account.analytic.account', string="Analytic Account")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('hod', 'HOD Approval'),
        ('manager', 'Accounts Approval'),
        ('coo', 'COO Approval'),
        ('ceo', 'CEO Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ('reject', 'Reject'),
    ], string='Status')
    payment_mode = fields.Many2many('payment.mode', string="Payment Mode")
    start_date = fields.Date(string='Start Date', default=datetime.date.today())
    end_date = fields.Date(string='End Date', default=datetime.date.today())