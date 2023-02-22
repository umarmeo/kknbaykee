from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PartyWisePurchaseReportTemplate(models.AbstractModel):
    _name = 'report.purchase_reports_baykee.party_wise_purchase_temp'
    _description = 'Party Wise Purchase Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_temp = []
        docs = self.env['party.wise.purchase.report'].browse(docids[0])
        company_id = self.env.user.company_id
        vendor_id = docs.partner_id.ids if docs.partner_id else []
        analytic_account = docs.analytic_account_id.ids if docs.analytic_account_id else []
        analytic_tags = docs.analytic_tag_ids.ids if docs.analytic_tag_ids else []
        products = docs.product_id.id if docs.product_id else []
        if docs.report_type == 'vendor_wise':
            vendor_domain = []
            if vendor_id:
                vendor_domain += [('id', 'in', vendor_id)]
            vendors = self.env['res.partner'].search(vendor_domain)
            for vendor in vendors:
                temp = []
                domain = [('order_id.date_order', '>=', docs.start_date), ('order_id.date_order', '<=', docs.end_date),
                          ('partner_id', '=', vendor.id)]
                if products:
                    domain.append(('product_id', 'in', products))
                purchase_order_line = self.env['purchase.order.line'].search(domain).sorted(key=lambda r: r.order_id.date_order)
                for line in purchase_order_line:
                    product_variant = [var.name for var in line.product_id.product_template_variant_value_ids]
                    result = ', '.join(product_variant)
                    vals = {
                        'product': line.product_id.name + ' ' + result,
                        'po': line.order_id.name,
                        'quantity': line.product_qty,
                        'unit_price': line.price_unit,
                        'price_total': line.price_subtotal,
                        'order_date': line.order_id.date_order,
                    }
                    temp.append(vals)
                temp2 = temp
                data_temp.append([vendor.name, temp2])
        if docs.report_type == 'division':
            division_domain = []
            if analytic_tags:
                division_domain += [('id', 'in', analytic_tags)]
            analytic_tags_id = self.env['account.analytic.tag'].search(division_domain)
            for tags in analytic_tags_id:
                temp = []
                domain = [('order_id.date_order', '>=', docs.start_date), ('order_id.date_order', '<=', docs.end_date),
                          ('order_id.analytic_tag_ids', '=', tags.id)]
                if products:
                    domain.append(('product_id', 'in', products))
                purchase_order_line = self.env['purchase.order.line'].search(domain).sorted(
                    key=lambda r: r.order_id.date_order)
                for line in purchase_order_line:
                    product_variant = [var.name for var in line.product_id.product_template_variant_value_ids]
                    result = ', '.join(product_variant)
                    vals = {
                        'vendor': line.order_id.partner_id.name,
                        'po': line.order_id.name,
                        'product': line.product_id.name + ' ' + result,
                        'quantity': line.product_qty,
                        'unit_price': line.price_unit,
                        'price_total': line.price_subtotal,
                        'order_date': line.order_id.date_order,
                    }
                    temp.append(vals)
                temp2 = temp
                data_temp.append([tags.name, temp2])
        if docs.report_type == 'project':
            project_domain = []
            if analytic_account:
                project_domain += [('id', 'in', analytic_account)]
            analytic_account_id = self.env['account.analytic.account'].search(project_domain)
            for account in analytic_account_id:
                temp = []
                domain = [('order_id.date_order', '>=', docs.start_date), ('order_id.date_order', '<=', docs.end_date),
                          ('order_id.account_analytic_id', '=', account.id)]
                if products:
                    domain.append(('product_id', 'in', products))
                purchase_order_line = self.env['purchase.order.line'].search(domain).sorted(
                    key=lambda r: r.order_id.date_order)
                for line in purchase_order_line:
                    product_variant = [var.name for var in line.product_id.product_template_variant_value_ids]
                    result = ', '.join(product_variant)
                    vals = {
                        'vendor': line.order_id.partner_id.name,
                        'po': line.order_id.name,
                        'product': line.product_id.name + ' ' + result,
                        'quantity': line.product_qty,
                        'unit_price': line.price_unit,
                        'price_total': line.price_subtotal,
                        'order_date': line.order_id.date_order,
                    }
                    temp.append(vals)
                temp2 = temp
                data_temp.append([account.name, temp2])
        return {
            'doc_ids': self.ids,
            'doc_model': 'purchase.order.line',
            'dat': data_temp,
            'docs': docs,
            'company_id': company_id,
            'data': data,
            'analytic_accounts': docs.analytic_account_id,
            'analytic_tags': docs.analytic_tag_ids,

        }
