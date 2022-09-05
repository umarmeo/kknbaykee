# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['analytic_tag_ids'] = ", s.analytic_tag_ids as analytic_tag_ids"
        groupby += ', s.analytic_tag_ids'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
