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
        usd_rate = docs.usd_rate
        temp = []
        products = self.env['product.product'].search([])
        for product in products:
            domain = [('order_id.date_order', '>=', start_date), ('order_id.date_order', '<=', end_date),
                      ('product_id', '=', product.id)]
            purchase_order_line = self.env['purchase.order.line'].search(domain, limit=1, order='create_date desc')
            for line in purchase_order_line:
                landed_cost_in_usd = int(line.price_unit) / usd_rate
                after_markup = landed_cost_in_usd + ((landed_cost_in_usd * markup) / 100)
                new_price = after_markup * usd_rate
                difference = new_price - line.price_unit
                vals = {
                    'product': line.product_id.name,
                    'unit_price': line.price_unit,
                    'landed_cost_in_usd': landed_cost_in_usd,
                    'after_markup': after_markup,
                    'new_price': new_price,
                    'difference': difference,
                }
                temp.append(vals)
        temp2 = temp
        data_temp.append(
            [usd_rate, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'm': markup,
            'markup': "After %s" % markup + "% Markup",
            'data': data,
        }
