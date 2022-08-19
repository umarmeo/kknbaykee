from odoo import api, models, fields


class PaymentReport(models.AbstractModel):
    _name = 'report.update_payment_process_module_baykee.payment_report'
    _description = 'Payment Process Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['payment.process'].search([('id', 'in', docids)])

        return {
            'doc_model': 'payment.process',
            'data': data,
            'docs': docs,
        }
