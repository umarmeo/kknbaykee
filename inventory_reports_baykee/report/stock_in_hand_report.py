from odoo import api, fields, models
from datetime import datetime

class StockInHandTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.stock_in_hand_report'
    _description = 'Stock In Hand Template'

    @api.model
    def _get_report_values(self, docids, data=None):

        data_temp = []
        docs = self.env['stock.in.hand.wizard'].browse(docids[0])
        date = docs.date
        product = docs.product_ids.ids if docs.product_ids else []
        location = docs.location_id
        # location_name = docs.location_id.complete_name
        loc_domain = [('usage', '=', 'internal')]
        loc_list = []
        if location:
            loc_domain += [('id', '=', location.id)]
        location_search = self.env['stock.location'].search(loc_domain)
        for loc in location_search:
            temp = []
            domain = [('new_date', '<=', date),
                      ('location_id', '=', loc.id)]
            if product:
                domain.append(('product_id', '=', product))
            stock = self.env['stock.quant'].search(domain).sorted(key=lambda r: r.new_date)
            for rec in stock:
                vals = {
                    'pro': rec.product_id.name,
                    'categ': rec.product_categ_id.name,
                    'lot': rec.lot_id.name,
                    'inv_qty_auto': rec.inventory_quantity_auto_apply,
                    'ava_qty': rec.available_quantity,
                    'pro_uom': rec.product_uom_id.name,
                    'value': rec.value,
                }
                temp.append(vals)
            temp2 = temp
            data_temp.append(
                [loc.complete_name, temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'stock.in.hand.wizard',
            'dat': data_temp,
            'docs': docs,
            'data': data,
        }