from odoo import api, fields, models
from datetime import datetime


class DeadStockReportTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.dead_stock_report'
    _description = 'Dead Stock Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        domain = []
        docs = self.env['dead.stock.wiz'].browse(docids[0])
        company_id = self.env.user.company_id
        locations = [l.id for l in docs.location_id]
        names = " "
        for loc in docs.location_id:
            name1 = loc.name
            name2 = loc.location_id.name
            name = name2 + "/" + name1
            names = names + name
            names = names + ","
        names = names.rstrip(',')
        domain.append(('location_id', 'in', locations))
        location_dest_ids = []
        dest = self.env['stock.location'].search([('usage', '=', 'customer')])
        for i in dest:
            location_dest_ids.append(i.id)
        domain.append(('location_dest_id', 'in', location_dest_ids))
        products = self.env['product.product'].search([])
        for product in products:
            temp = []
            stock_moves = self.env['stock.move'].search(
                domain + [('state', '=', 'done'), ('product_id', '=', product.id),
                          ('date', '<=', docs.end_date), ('date', '>', docs.start_date)])
            print(stock_moves)
            if not stock_moves:
                product_variant = [var.name for var in product.product_template_variant_value_ids]
                result = ', '.join(product_variant)
                vals = {
                    'name': str(product.name) + ' ' + result,
                    'sale_price': product.lst_price,
                    'cost_price': product.standard_price
                }
                qty = 0
                for x in locations:
                    for quant in product.stock_quant_ids:
                        if quant.location_id.id == x:
                            qty = qty + quant.quantity
                vals['quantity'] = qty
                if qty > 0:
                    temp.append(vals)
            temp2 = temp
            data_temp.append(
                [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'dead.stock.wiz',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'names': names,
            'company_id': company_id,
        }
