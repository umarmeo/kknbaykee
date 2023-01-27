from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CustomerWiseSaleReportTemplate(models.AbstractModel):
    _name = 'report.sale_reports_baykee.cus_wise_sale_temp'
    _description = 'Customer Wise Sale Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):

        data_temp = []
        docs = self.env['cus.wise.sale.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        customer = docs.partner_id.ids if docs.partner_id else []
        analytic_account = docs.analytic_account_id.ids if docs.analytic_account_id else []
        analytic_tag = docs.analytic_tag_id.ids if docs.analytic_tag_id else []
        product_id = docs.product_id.ids if docs.product_id else []
        cus_domain = []
        if customer:
            cus_domain += [('id', 'in', customer)]
        customer_search = self.env['res.partner'].search(cus_domain)
        for cus in customer_search:
            temp = []
            domain = [('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date),
                      ('order_partner_id', '=', cus.id), ('order_id.state', '=', 'sale')]
            if product_id:
                domain.append(('product_id', 'in', product_id))
            if analytic_account:
                domain.append(('analytic_account_id', 'in', analytic_account))
            if analytic_tag:
                domain.append(('analytic_tag_ids', 'in', analytic_tag))
            sale_order_line = self.env['sale.order.line'].search(domain)
            for line in sale_order_line:
                product_variant = [var.name for var in line.product_id.product_template_variant_value_ids]
                result = ', '.join(product_variant)
                invoice = self.env['account.move'].search([('invoice_origin', '=', line.order_id.name), ('ref', 'not ilike', 'Reversal of'), ('state', '=', 'posted')])
                vals = {
                    'so': line.order_id.name,
                    'product': str(line.product_id.name) + ' ' + result,
                    'quantity': line.product_uom_qty,
                    'unit_price': line.price_unit,
                    'total_price': line.price_subtotal,
                    'order_date': invoice.invoice_date,
                }
                if invoice:
                    temp.append(vals)
            temp2 = temp
            data_temp.append(
                [cus.name, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'cus.wise.sale.report',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
