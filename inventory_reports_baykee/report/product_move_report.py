from odoo import api, fields, models
from datetime import datetime


class ProductMoveReportTemplate(models.AbstractModel):
    _name = 'report.inventory_reports_baykee.product_move_report'
    _description = 'Product Move Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['product.move.wiz'].browse(docids[0])
        company_id = self.env.user.company_id
        products = docs.product_id.ids if docs.product_id else []
        analytic_account = docs.analytic_account_id.ids if docs.analytic_account_id else []
        analytic_tag = docs.analytic_tag_id.ids if docs.analytic_tag_id else []
        product_domain = []
        if products:
            product_domain.append(('id', 'in', products))
        product_search = self.env['product.product'].search(product_domain)
        for product in product_search:
            stock_quantity = 0
            stock_price = 0
            stock_total = 0
            purchase_quantity = 0
            purchase_price = 0
            purchase_total = 0
            purchase_return_qty = 0
            purchase_return_price = 0
            purchase_return_total = 0
            sale_quantity = 0
            sale_price = 0
            sale_total = 0
            sale_return_qty = 0
            sale_return_price = 0
            sale_return_total = 0
            ho_warehouse_who_qty = 0
            ho_warehouse_fwh_qty = 0
            fwh_warehouse_who_qty = 0
            fwh_warehouse_fwh_qty = 0
            purchases_domain = [('product_id', '=', product.id), ('order_id.date_order', '>=', docs.start_date),
                                ('order_id.date_order', '<=', docs.end_date)]
            purchase_return_domain = [('product_id', '=', product.id), ('move_id.move_type', '=', 'in_refund'),
                                      ('move_id.date', '>=', docs.start_date), ('move_id.date', '<=', docs.end_date)]
            sales_domain = [('product_id', '=', product.id), ('order_id.date_order', '>=', docs.start_date),
                            ('order_id.date_order', '<=', docs.end_date)]
            sales_return_domain = [('product_id', '=', product.id), ('move_id.move_type', '=', 'out_refund'),
                                   ('move_id.date', '>=', docs.start_date), ('move_id.date', '<=', docs.end_date)]
            if analytic_account:
                purchases_domain.append(('order_id.account_analytic_id', 'in', analytic_account))
                purchase_return_domain.append(('analytic_account_id', 'in', analytic_account))
                sales_domain.append(('analytic_account_id', 'in', analytic_account))
                sales_return_domain.append(('analytic_account_id', '=', analytic_account))
            stock_quant = self.env['product.product'].search([('id', '=', product.id)])
            for stock in stock_quant:
                stock_quantity += stock.qty_available
                stock_price = stock.standard_price
                stock_total = stock_quantity * stock_price
            purchases = self.env['purchase.order.line'].search(purchases_domain)
            for purchase in purchases:
                purchase_quantity += purchase.product_qty
                purchase_price = purchase.product_id.standard_price
                purchase_total = purchase_quantity * purchase_price
            purchase_returns = self.env['account.move.line'].search(purchase_return_domain)
            for pur_return in purchase_returns:
                purchase_return_qty += pur_return.quantity
                purchase_return_price = pur_return.product_id.standard_price
                purchase_return_total = purchase_return_qty * purchase_return_price
            sales = self.env['sale.order.line'].search(sales_domain)
            for sale in sales:
                sale_quantity += sale.product_uom_qty
                sale_price = sale.price_unit
                sale_total = sale_quantity * sale_price
            sale_returns = self.env['account.move.line'].search(sales_return_domain)
            for sale_return in sale_returns:
                sale_return_qty += sale_return.quantity
                sale_return_price = sale_return.product_id.lst_price
                sale_return_total = sale_return_qty * sale_return_price
            ho_warehouse = self.env['stock.move'].search(
                [('product_id', '=', product.id), ('location_id.location_id.name', 'ilike', 'FWH'),
                 ('location_dest_id.location_id.name', 'ilike', 'WHO')])
            for who in ho_warehouse:
                ho_warehouse_who_qty += who.product_uom_qty
                ho_warehouse_fwh_qty += who.product_uom_qty
            fwh_warehouse = self.env['stock.move'].search(
                [('product_id', '=', product.id), ('location_id.location_id.name', 'ilike', 'WHO'),
                 ('location_dest_id.location_id.name', 'ilike', 'FWH')])
            for fwh in fwh_warehouse:
                fwh_warehouse_who_qty += fwh.product_uom_qty
                fwh_warehouse_fwh_qty += fwh.product_uom_qty
            final_who_qty = ho_warehouse_who_qty - fwh_warehouse_who_qty
            final_fwh_qty = - ho_warehouse_fwh_qty + fwh_warehouse_fwh_qty
            closing_stock_quantity = ((((stock_quantity + purchase_quantity) - purchase_return_qty) - sale_quantity) + sale_return_qty)
            closing_stock_price = product.standard_price
            closing_stock_total = closing_stock_quantity * closing_stock_price
            product_variant = [var.name for var in product.product_template_variant_value_ids]
            result = ', '.join(product_variant)
            temp = []
            vals = {
                'product': product.name + ' ' + result,
                'stock_quantity': stock_quantity,
                'stock_price': stock_price,
                'stock_total': stock_total,
                'purchase_quantity': purchase_quantity,
                'purchase_price': purchase_price,
                'purchase_total': purchase_total,
                'purchase_return_qty': purchase_return_qty,
                'purchase_return_price': purchase_return_price,
                'purchase_return_total': purchase_return_total,
                'sale_quantity': sale_quantity,
                'sale_price': sale_price,
                'sale_total': sale_total,
                'sale_return_qty': sale_return_qty,
                'sale_return_price': sale_return_price,
                'sale_return_total': sale_return_total,
                'final_who_qty': final_who_qty,
                'final_fwh_qty': final_fwh_qty,
                'closing_stock_quantity': closing_stock_quantity,
                'closing_stock_price': closing_stock_price,
                'closing_stock_total': closing_stock_total,
            }
            temp.append(vals)
            temp2 = temp
            data_temp.append(
                [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'stock.in.hand.wizard',
            'dat': data_temp,
            'docs': docs,
            'data': data,
            'company_id': company_id,
        }
