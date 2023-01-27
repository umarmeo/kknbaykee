from odoo import api, fields, models
from datetime import datetime


class DeliveryReportTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.delivery_report'
    _description = 'Delivery Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['delivery.report.wiz'].browse(docids[0])
        company_id = self.env.user.company_id
        partner_id = docs.partner_id.ids if docs.partner_id else []
        analytic_account = docs.analytic_account_id.ids if docs.analytic_account_id else []
        analytic_tag = docs.analytic_tag_id.ids if docs.analytic_tag_id else []
        partner_domain = []
        if partner_id:
            partner_domain.append(('id', 'in', partner_id))
        partners = self.env['res.partner'].search(partner_domain)
        for partner in partners:
            temp = []
            temp1 = []
            deliveries = self.env['stock.picking'].search(
                [('scheduled_date', '>=', docs.start_date), ('scheduled_date', '<=', docs.end_date),
                 ('state', '=', 'done'), ('partner_id', '=', partner.id)])
            for delivery in deliveries:
                sale_domain = [('name', '=', delivery.origin)]
                if analytic_account:
                    sale_domain.append(('analytic_account_id', 'in', analytic_account))
                if analytic_tag:
                    sale_domain.append(('analytic_tag_ids', 'in', analytic_tag))
                sale_order = self.env['sale.order'].search(sale_domain)
                for sale in sale_order:
                    vals = {
                        'ref': delivery.name,
                        'source_loc': delivery.location_id.name,
                        'customer': delivery.partner_id.name,
                        'date': delivery.scheduled_date,
                        'dead_date': delivery.date_deadline,
                        'transfer_date': delivery.date_done,
                        'source_doc': sale.name,
                        'status': delivery.state,
                    }
                    temp.append(vals)
                pur_domain = [('name', '=', delivery.origin)]
                if analytic_account:
                    pur_domain.append(('account_analytic_id', 'in', analytic_account))
                if analytic_tag:
                    sale_domain.append(('analytic_tag_ids', 'in', analytic_tag))
                pur_order = self.env['purchase.order'].search(pur_domain)
                for pur in pur_order:
                    vals = {
                        'ref': delivery.name,
                        'source_loc': delivery.location_id.name,
                        'customer': delivery.partner_id.name,
                        'date': delivery.scheduled_date,
                        'dead_date': delivery.date_deadline,
                        'transfer_date': delivery.date_done,
                        'source_doc': pur.name,
                        'status': delivery.state,
                    }
                    temp1.append(vals)
            temp2 = temp + temp1
            data_temp.append(
                [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'delivery.report.wiz',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'company_id': company_id,
        }
