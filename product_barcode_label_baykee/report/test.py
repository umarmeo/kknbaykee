from collections import defaultdict
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductLabelTemplate(models.AbstractModel):
    _name = 'report.product_barcode_label_baykee.product_label_temp'
    _description = 'Product Label Report'

    def _get_report_values(self, docids, data):
        data_temp = []
        docs = self.env['product.label.baykee'].browse(docids[0])
        quantity = docs.quantity
        extra_content = docs.extra_content
        is_lot_serial = docs.is_lot_serial
        product_variant = docs.product_variant.ids
        active_model = ''
        if docs.product_tmpl_ids:
            products = docs.product_tmpl_ids.ids
            active_model = 'product.template'
        elif docs.product_ids:
            products = docs.product_ids.ids
            active_model = 'product.product'
        product_search = self.env[active_model].search([('id', 'in', products)])
        temp = []
        for product in product_search:
            if product_variant:
                variants = self.env['product.product'].search([('id', 'in', product_variant)])
                i = 0
                simple = []
                for var in variants:
                    var_attrs = [v.name for v in var.product_template_variant_value_ids]
                    new_lst = (', '.join(var_attrs))
                    if is_lot_serial == '0':
                        vals = {
                            'product': product.name,
                            'barcode': var.barcode,
                            'variant': new_lst,
                            'content': extra_content,
                        }
                        for loop in range(quantity):
                            if i % 4 == 0:
                                temp.append(simple)
                                simple = []
                            simple.append(vals)
                            i += 1
                if len(simple) > 0:
                    for j in range(len(simple), 4):
                        simple.append({
                            'product': False,
                            'barcode': False,
                            'variant': False,
                            'content': False,
                        })
                    temp.append(simple)
                    simple = []
                    if is_lot_serial == '1':
                        lot_id = product.product_variant_id.stock_quant_ids.lot_id
                        i = 0
                        simple = []
                        for rec in lot_id:
                            vals = {
                                'product': product.name,
                                'barcode': product.barcode,
                                'serial': rec.name,
                                'content': extra_content,
                            }
                            for loop in range(quantity):
                                if i % 4 == 0:
                                    temp.append(simple)
                                    simple = []
                                simple.append(vals)
                                i += 1
                        if len(simple) > 0:
                            for j in range(len(simple), 4):
                                simple.append({
                                    'product': False,
                                    'barcode': False,
                                    'serial': False,
                                    'content': False,
                                })
                                temp.append(simple)
                                simple = []
            else:
                if is_lot_serial == '0':
                    simple = []
                    vals = {
                        'product': product.name,
                        'barcode': product.barcode,
                        'content': extra_content,
                    }
                    i = 0
                    for loop in range(quantity):
                        if i % 4 == 0:
                            temp.append(simple)
                            simple = []
                        simple.append(vals)
                        i += 1
                    if len(simple) > 0:
                        for j in range(len(simple), 4):
                            simple.append({
                                'product': False,
                                'barcode': False,
                                'content': False,
                            })
                        temp.append(simple)
                if is_lot_serial == '1':
                    lot_id = product.product_variant_id.stock_quant_ids.lot_id
                    i = 0
                    simple = []
                    for rec in lot_id:
                        vals = {
                            'product': product.name,
                            'barcode': product.barcode,
                            'serial': rec.name,
                            'content': extra_content,
                        }
                        for loop in range(quantity):
                            if i % 4 == 0:
                                temp.append(simple)
                                simple = []
                            simple.append(vals)
                            i += 1
                    if len(simple) > 0:
                        for j in range(len(simple), 4):
                            simple.append({
                                'product': False,
                                'barcode': False,
                                'serial': False,
                                'content': False,
                            })
                            temp.append(simple)
                            simple = []
            temp2 = temp
            print(temp2)
            data_temp.append(
                [temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'product.label.baykee',
            'dat': data_temp,
            'active_model': active_model,
            'quantity': quantity,
            'is_lot_serial': is_lot_serial,
            'docs': docs,
            'data': data,
        }
