from odoo import api, fields, models
from datetime import datetime

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
            domain += [('new_date', '=', date)]
        stock = self.env['stock.move.line'].search(domain)
        print(stock)
        for rec in stock:
            main.append({
                'date': rec.date,
                'ref': rec.reference,
                'pro': rec.product_id.name,
                'lot': rec.lot_id.name,
                'loc_id': rec.location_id.name,
                'loc_dest': rec.location_dest_id.name,
                'qty_done': rec.qty_done,
                'pro_uom': rec.product_uom_id.name,
                'state': rec.state,
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
