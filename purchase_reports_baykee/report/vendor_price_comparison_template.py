from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class VendorPriceComparisonReportTemplate(models.AbstractModel):
    _name = 'report.purchase_reports_baykee.vendor_price_comparison_temp'
    _description = 'Vendor Price Comparison Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['vendor.price.comparison.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        vendors = docs.partner_id.ids if docs.partner_id else []
        product_id = docs.product_id
        prod_domain = []
        product_list = []
        for p in product_id:
            product_list.append(p.id)
        if product_list:
            prod_domain += [('id', 'in', product_list)]
        products_search = self.env['product.product'].search(prod_domain)
        for product in products_search:
            temp = []
            domain = [('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date),
                      ('product_id', '=', product.id)]
            if vendors:
                domain.append(('salesman_id', '=', vendors))
            purchase_order_line = self.env['purchase.order.line'].search(domain).sorted(key=lambda r: r.partner_id)
            for line in purchase_order_line:
                vals = {
                    'vendor': line.partner_id.name,
                    'quantity': line.product_qty,
                    'unit_price': line.price_unit,
                    'order_date': line.order_id.date_order,
                }
                temp.append(vals)
            temp2 = temp
            data_temp.append(
                [product.name, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
