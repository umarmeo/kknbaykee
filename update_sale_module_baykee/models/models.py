# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class update_sale_module_baykee(models.Model):
    _inherit = 'sale.order'

    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade',
                                 readonly=True)
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_get_invoice_status', store=True)

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoice_status(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.
        """
        unconfirmed_orders = self.filtered(lambda so: so.state not in ['sale', 'done'])
        unconfirmed_orders.invoice_status = 'no'
        confirmed_orders = self - unconfirmed_orders
        if not confirmed_orders:
            return
        line_invoice_status_all = [
            (d['order_id'][0], d['invoice_status'])
            for d in self.env['sale.order.line'].read_group([
                ('order_id', 'in', confirmed_orders.ids),
                ('is_downpayment', '=', False),
                ('display_type', '=', False),
            ],
                ['order_id', 'invoice_status'],
                ['order_id', 'invoice_status'], lazy=False)]
        for order in confirmed_orders:
            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]
            if order.state not in ('sale', 'done'):
                order.invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                order.invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                order.invoice_status = 'invoiced'
            elif line_invoice_status and all(
                    invoice_status in ('invoiced', 'upselling') for invoice_status in line_invoice_status):
                order.invoice_status = 'upselling'
            else:
                order.invoice_status = 'no'

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale'
        }

    @api.onchange('analytic_account_id', 'analytic_tag_ids')
    def _onchange_sale_order_analytic(self):
        for line in self.order_line:
            line.analytic_account_id = self.analytic_account_id
            line.analytic_tag_ids = self.analytic_tag_ids

    def action_data_send(self):
        duplicate_list = [self.analytic_account_id, self.analytic_tag_ids]
        return duplicate_list

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        if self.order_line:
            for rec in self.order_line:
                if rec.price_unit < rec.min_sale_price:
                    raise UserError(_('Unit price %s of %s must be less than or equal to Minimum Sale Price %s'
                                      % (rec.price_unit, rec.product_id.name, rec.min_sale_price)))

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)
        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True


class update_sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2one('account.analytic.tag', string='Analytic Tags')
    state = fields.Selection(
        related='order_id.state', string='Order Status', copy=False, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True,
                               copy=False)
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        ondelete="set null", tracking=True,
        change_default=True, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user)
    min_sale_price = fields.Float(string="Minimum Sale Price", related='product_id.min_sale_price')

    @api.onchange('analytic_account_id', 'analytic_tag_ids', 'order_id')
    def _onchange_sale_order_line(self):
        list_receive = self.order_id.action_data_send()
        self.analytic_account_id = list_receive[0]
        self.analytic_tag_ids = list_receive[1]

    # @api.onchange('price_unit')
    # def onchange_price_unit(self):
    #     for rec in self:
    #         if rec.price_unit > 0:
    #             if rec.price_unit > rec.min_sale_price:
    #                 raise UserError(_('Unit price must be less than or equal to Minimum Sale Price'))
