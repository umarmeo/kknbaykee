from odoo import fields, models, api


class PendingDeliveryReportWizard(models.TransientModel):
    _name = 'pending.delivery.wiz'
    _description = 'Pending Delivery Report Wizard'

    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', default=fields.Date.context_today)
