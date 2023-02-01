from odoo import api, fields, models
from datetime import datetime
from dateutil import relativedelta


class SlowMoveReportTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.slow_move_report'
    _description = 'Slow Move Stock Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        domain = []
        docs = self.env['slow.move.wiz'].browse(docids[0])
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
            total_qty = 0
            temp = []
            stock_moves = self.env['stock.move'].search(
                domain + [('state', '=', 'done'), ('product_id', '=', product.id),
                          ('date', '<=', docs.end_date), ('date', '>', docs.start_date)])
            if stock_moves:
                qty = 0
                for x in locations:
                    for quant in product.stock_quant_ids:
                        if quant.location_id.id == x:
                            qty = qty + quant.quantity
                if qty > 0:
                    for move in stock_moves:
                        total_qty += move.product_uom_qty
                    delta = relativedelta.relativedelta(docs.end_date, docs.start_date)
                    months = delta.months
                    avg_sale_qty = total_qty / months
                    product_variant = [var.name for var in product.product_template_variant_value_ids]
                    result = ', '.join(product_variant)
                    stock_cover = qty / avg_sale_qty
                    if stock_cover > 3:
                        vals = {
                            'name': str(product.name) + ' ' + result,
                            'sale_price': product.lst_price,
                            'cost_price': product.standard_price,
                            'quantity': qty,
                            'stock_cover': stock_cover,
                        }
                        temp.append(vals)
            temp2 = temp
            data_temp.append(
                [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'slow.move.wiz',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'names': names,
            'company_id': company_id,
        }
