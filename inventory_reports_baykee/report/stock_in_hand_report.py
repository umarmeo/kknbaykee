from odoo import api, fields, models


class StockInHandTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.stock_in_hand_report'
    _description = 'Stock In Hand Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.in.hand.wizard'].browse(docids[0])
        domain = []
        new_products = []
        location = docs.location_id
        products = docs.product_ids
        date = docs.date
        main = []
        for product in products:
            new_products.append(product.id)
        if location:
            domain += [('location_id', '=', location.id)]
        if products:
            domain += [('product_id', 'in', new_products)]
        if date:
            domain += [('inventory_date', '=', date)]
        stock = self.env['stock.quant'].search(domain)
        for rec in stock:
            main.append({
                'loc': rec.location_id.name,
                'pro': rec.product_id.name,
                'categ': rec.product_categ_id.name,
                'lot': rec.lot_id.name,
                'inv_qty_auto': rec.inventory_quantity_auto_apply,
                'ava_qty': rec.available_quantity,
                'pro_uom': rec.product_uom_id.name,
                'value': rec.value,
            })


        report = self.env['ir.actions.report']._get_report_from_name(
            'inventory_reports_baykee.stock_in_hand_report')
        docargs = {
            'doc_ids': [],
            'doc_model': 'stock.in.hand.wizard',
            'data': data,
            'docs': docs,
            'main': main,
        }
        return docargs
