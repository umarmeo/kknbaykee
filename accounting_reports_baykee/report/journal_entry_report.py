from odoo import api, models, fields


class JournalEntryReport(models.AbstractModel):
    _name = 'report.accounting_reports_baykee.journal_entry_voucher'
    _description = 'Journal Entry Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].search([('id', 'in', docids)])
        # if docs.name.find('BRV/') != -1:
        #     vals = 'Bank Receipt Voucher'
        # elif docs.name.find('CRV/') != -1:
        #     vals = 'Cash Receipt Voucher'
        # elif docs.name.find('BPV/') != -1:
        #     vals = 'Bank Payment Voucher'
        # elif docs.name.find('CPV/') != -1:
        #     vals = 'Cash Payment Voucher'
        # elif docs.name.find('JV') != -1:
        #     vals = 'JV Report'
        # el
        if docs.journal_id:
            if docs.journal_id.type == 'sale' and docs.amount_tax_signed == 0:
                vals = 'Non Tax Sale Report'
            elif docs.journal_id.type == 'sale' and docs.amount_tax_signed != 0:
                vals = 'Tax Sale Report'
            elif docs.journal_id.type == 'purchase' and docs.amount_tax_signed == 0:
                vals = 'Non Tax Payment Report'
            elif docs.journal_id.type == 'purchase' and docs.amount_tax_signed != 0:
                vals = 'Tax Payment Report'
            elif docs.journal_id.type == 'bank':
                vals = 'Bank Voucher'
            elif docs.journal_id.type == 'cash':
                vals = 'Cash Voucher'
            else:
                vals = '%s Report' % docs.journal_id.name
        else:
            vals = '%s Report' % "Undefined"
        return {
            'doc_model': 'account.move',
            'data': data,
            'docs': docs,
            'vals': vals,
        }
