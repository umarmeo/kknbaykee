from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SalePersonWiseSaleReportTemplate(models.AbstractModel):
    _name = 'report.sale_reports_baykee.sale_person_wise_sale_temp'
    _description = 'Sale Person Wise Sale Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):

        data_temp = []
        docs = self.env['sale.person.wise.sale.report'].browse(docids[0])
        company_id = self.env.user.company_id
        start_date = docs.start_date
        end_date = docs.end_date
        sale_person = docs.sale_person.ids if docs.sale_person else []
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
            if sale_person:
                domain.append(('salesman_id', '=', sale_person))
            sale_order_line = self.env['sale.order.line'].search(domain).sorted(key=lambda r: r.salesman_id)
            for line in sale_order_line:
                vals = {
                    'sale_person': line.salesman_id.name,
                    'quantity': line.product_uom_qty,
                    'unit_price': line.price_unit,
                    'order_date': line.order_id.date_order,
                }
                temp.append(vals)
            temp2 = temp
            data_temp.append(
                [product.name, temp2, start_date, end_date])
        return {
            'doc_ids': self.ids,
            'doc_model': 'general.ledger',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
