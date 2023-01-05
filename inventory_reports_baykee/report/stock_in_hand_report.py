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
        loc_domain = [('usage', '=', 'internal')]
        if location:
            loc_domain += [('id', '=', location.id)]
        location_search = self.env['stock.location'].search(loc_domain)
        for loc in location_search:
            temp = []
            domain = [('new_date', '<=', date),
                      ('location_id', '=', loc.id)]
            if product:
                domain.append(('product_id', '=', product))
            available_qty = 0
            inventory_qty = 0
            stock = self.env['stock.quant'].search(domain).sorted(key=lambda r: r.new_date)
            val = {}
            for rec in stock:
                available_qty += rec.available_quantity
                inventory_qty += rec.inventory_quantity
                product_variant = [var.name for var in rec.product_id.product_template_variant_value_ids]
                result = ', '.join(product_variant)
                key = rec.product_id.id
                if key not in val:
                    val[key] = {
                        'product_id': rec.product_id.id,
                        'pro': rec.product_id.name + ' ' + result,
                        'categ': rec.product_categ_id.name,
                        'ava_qty': rec.available_quantity,
                        'pro_uom': rec.product_uom_id.name,
                        'value': rec.value,
                    }
                    temp.append(val[key])
                else:
                    val[key].update({
                        'ava_qty': val[key].get('ava_qty') + rec.available_quantity,
                    })
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