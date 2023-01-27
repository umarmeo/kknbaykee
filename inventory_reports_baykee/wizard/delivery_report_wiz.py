from odoo import fields, models, api


class DeliveryReportWizard(models.TransientModel):
    _name = 'delivery.report.wiz'
    _description = 'Delivery Report Wizard'

    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', default=fields.Date.context_today)
    partner_id = fields.Many2many('res.partner', string='Contact')
    analytic_account_id = fields.Many2many('account.analytic.account', string='Analytic Account')
    analytic_tag_id = fields.Many2many('account.analytic.tag', string='Analytic Tags')
