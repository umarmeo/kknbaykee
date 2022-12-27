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
        analytic_account = docs.analytic_account_id.ids if docs.analytic_account_id else []
        analytic_tags = docs.analytic_tag_ids.ids if docs.analytic_tag_ids else []
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
                print(vendors)
                domain.append(('partner_id', 'in', vendors))
            if analytic_account:
                domain.append(('account_analytic_id', 'in', analytic_account))
            if analytic_tags:
                domain.append(('analytic_tag_ids', 'in', analytic_tags))
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
            product_variant = [var.name for var in product.product_template_variant_value_ids]
            result = ', '.join(product_variant)
            data_temp.append(
                [product.name + ' ' + result, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
