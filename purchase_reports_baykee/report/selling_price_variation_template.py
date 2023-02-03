from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SellingPriceVariationReportTemplate(models.AbstractModel):
    _name = 'report.purchase_reports_baykee.selling_price_variation_temp'
    _description = 'Selling Price Variation Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['selling.price.variation.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        markup = docs.markup
        product_id = docs.product_id.ids
        temp = []
        product_domain = []
        if product_id:
            product_domain += [('id', '=', product_id)]
        products = self.env['product.product'].search(product_domain)
        for product in products:
            domain = [('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date),
                      ('product_id', '=', product.id)]
            purchase_order_line = self.env['purchase.order.line'].search(domain, limit=1, order='create_date desc')
            after_markup = 0
            new_price = 0
            difference = 0
            for line in purchase_order_line:
                product_variant = [var.name for var in line.product_id.product_template_variant_value_ids]
                result = ', '.join(product_variant)
                if line.dollar_unit_price:
                    after_markup = line.dollar_unit_price + ((line.dollar_unit_price * markup) / 100)
                    new_price = after_markup * line.dollar_rate
                    difference = new_price - line.price_unit
                vals = {
                    'product': line.product_id.name + ' ' + result,
                    'dollar_rate': line.dollar_rate,
                    'unit_price': line.price_unit,
                    'landed_cost_in_usd': line.dollar_unit_price,
                    'after_markup': after_markup,
                    'new_price': new_price,
                    'difference': difference,
                }
                temp.append(vals)
        temp2 = temp
        data_temp.append(
            [temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'products': docs.product_id,
            'products_all': "All",
            'm': markup,
            'markup': "After %s" % markup + "% Markup",
            'data': data,
        }
