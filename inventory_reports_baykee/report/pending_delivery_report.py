from odoo import api, fields, models
from datetime import datetime


class PendingDeliveryReportTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.pending_delivery_report'
    _description = 'Pending Delivery Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['pending.delivery.wiz'].browse(docids[0])
        company_id = self.env.user.company_id
        deliveries = self.env['stock.picking'].search(
            [('scheduled_date', '>=', docs.start_date), ('scheduled_date', '<=', docs.end_date),
             ('state', '=', 'assigned')])
        for delivery in deliveries:
            temp = []
            vals = {
                'ref': delivery.name,
                'source_loc': delivery.location_id.name,
                'customer': delivery.partner_id.name,
                'responsible': delivery.user_id.name,
                'date': delivery.scheduled_date,
                'avail': delivery.products_availability,
                'dead_date': delivery.date_deadline,
                'transfer_date': delivery.date_done,
                'source_doc': delivery.origin,
                'back_order': delivery.backorder_id.name,
                'status': delivery.state,
            }
            temp.append(vals)
            temp2 = temp
            data_temp.append(
                [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'stock.in.hand.wizard',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'company_id': company_id,
        }
