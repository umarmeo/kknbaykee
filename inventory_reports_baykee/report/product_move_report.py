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
        product_domain = []
        if products:
            product_domain.append(('id', 'in', products))
        product_search = self.env['product.product'].search(product_domain)
        for product in product_search:
            open_stock_quantity = 0
            purchase_quantity = 0
            purchase_return_qty = 0
            sale_quantity = 0
            sale_return_qty = 0
            ho_warehouse_who_qty = 0
            ho_warehouse_fwh_qty = 0
            fwh_warehouse_who_qty = 0
            fwh_warehouse_fwh_qty = 0
            virtual_open_qty = 0
            virtual_open_qty1 = 0
            purchase_open_qty = 0
            purchase_return_open_qty = 0
            sale_open_qty = 0
            sale_return_open_qty = 0

            purchase_stock_open = self.env['stock.move.line'].search(
                [('date', '<', docs.start_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'supplier'), ('location_dest_id.usage', '=', 'internal')])
            for open_pur in purchase_stock_open:
                purchase_open_qty += open_pur.qty_done
            purchase_return_stock_open = self.env['stock.move.line'].search(
                [('date', '<', docs.start_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '=', 'supplier')])
            for open_pur_rt in purchase_return_stock_open:
                purchase_return_open_qty += open_pur_rt.qty_done
            sale_stock_open = self.env['stock.move.line'].search(
                [('date', '<', docs.start_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '=', 'customer')])
            for open_sal in sale_stock_open:
                sale_open_qty += open_sal.qty_done
            sale_return_stock_open = self.env['stock.move.line'].search(
                [('date', '<', docs.start_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'customer'), ('location_dest_id.usage', '=', 'internal')])
            for open_sal_rt in sale_return_stock_open:
                sale_return_open_qty += open_sal_rt.qty_done
            virtual_stock_open = self.env['stock.move.line'].search(
                [('date', '<', docs.start_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'internal'),
                 ('location_dest_id.usage', '=', 'inventory')])
            for open_virtual in virtual_stock_open:
                virtual_open_qty += open_virtual.qty_done
            print(virtual_open_qty)
            virtual_stock_open1 = self.env['stock.move.line'].search(
                [('date', '<', docs.start_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'inventory'),
                 ('location_dest_id.usage', '=', 'internal')])
            for open_virtual1 in virtual_stock_open1:
                virtual_open_qty1 += open_virtual1.qty_done
            print(virtual_open_qty1)
            open_stock_quantity = virtual_open_qty1 - virtual_open_qty + purchase_open_qty - purchase_return_open_qty - sale_open_qty + sale_return_open_qty
            open_stock_price = product.standard_price
            open_stock_total = open_stock_quantity * open_stock_price
            purchase_stock = self.env['stock.move.line'].search(
                [('date', '>=', docs.start_date), ('date', '<=', docs.end_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'supplier'), ('location_dest_id.usage', '=', 'internal')])
            for purchase in purchase_stock:
                purchase_quantity += purchase.qty_done
            purchase_price = product.standard_price
            purchase_total = purchase_quantity * purchase_price
            purchase_return_stock = self.env['stock.move.line'].search(
                [('date', '>=', docs.start_date), ('date', '<=', docs.end_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '=', 'supplier')])
            for purchase_return in purchase_return_stock:
                purchase_return_qty += purchase_return.qty_done
            purchase_return_price = product.standard_price
            purchase_return_total = purchase_return_qty * purchase_return_price
            sale_stock = self.env['stock.move.line'].search(
                [('date', '>=', docs.start_date), ('date', '<=', docs.end_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '=', 'customer')])
            for sale in sale_stock:
                sale_quantity += sale.qty_done
            sale_price = product.lst_price
            sale_total = sale_quantity * sale_price
            sale_return_stock = self.env['stock.move.line'].search(
                [('date', '>=', docs.start_date), ('date', '<=', docs.end_date), ('product_id', '=', product.id),
                 ('location_id.usage', '=', 'customer'), ('location_dest_id.usage', '=', 'internal')])
            for sale_return in sale_return_stock:
                sale_return_qty += sale_return.qty_done
            sale_return_price = product.lst_price
            sale_return_total = sale_quantity * sale_price
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
            closing_stock_quantity = open_stock_quantity + purchase_quantity - purchase_return_qty - sale_quantity + sale_return_qty
            closing_stock_price = product.standard_price
            closing_stock_total = closing_stock_quantity * closing_stock_price
            product_variant = [var.name for var in product.product_template_variant_value_ids]
            result = ', '.join(product_variant)
            temp = []
            vals = {
                'product': product.name + ' ' + result,
                'open_stock_quantity': open_stock_quantity,
                'open_stock_price': open_stock_price,
                'open_stock_total': open_stock_total,
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
