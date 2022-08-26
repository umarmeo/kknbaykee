from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        move.add_data()
        return move

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        print("hi i m write function")
        self.add_data()
        return res

    def add_data(self):
        tag_ids = []
        analytic_account = []
        label = []
        for line in self.line_ids:
            label = self.invoice_origin
            if not line.name:
                line.write({'name': label})
            if line.analytic_tag_ids:
                tag_ids = line.analytic_tag_ids
                analytic_account = line.analytic_account_id
            if tag_ids:
                for tag_id in tag_ids:
                    line.write({'analytic_tag_ids': [(4, tag_id.id)]})
            if analytic_account:
                for account_id in analytic_account:
                    line.write({'analytic_account_id': account_id.id})

