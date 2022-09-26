from odoo import models


class GeneralLedgerXlsx(models.AbstractModel):
    _name = 'report.accounting_reports_baykee.general_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, main):
        sheet = workbook.add_worksheet('General Ledger XLSX Report')
        bold = workbook.add_format({'bold': True})
        title_format1 = workbook.add_format(
            {'bold': True, 'font_color': '#000000', 'bg_color': '#f48531', 'font_size': 14, 'border': 1,
             'align': 'center', 'valign': 'vcenter'})
        title_format2 = workbook.add_format(
            {'bold': True, 'font_color': '#000000', 'bg_color': '#f48531', 'font_size': 10, 'border': 1,
             'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'font_color': '#ffffff', 'bg_color': '#f48531'})

        row = 5
        col = 0

        sheet.set_column(row, col, 20)
        sheet.set_column(row, col + 1, 20)
        sheet.set_column(row, col + 2, 20)
        sheet.set_column(row, col + 3, 20)
        sheet.set_column(row, col + 4, 20)
        sheet.set_column(row, col + 5, 20)
        sheet.set_column(row, col + 6, 20)
        sheet.set_column(row, col + 7, 20)
        sheet.set_column(row, col + 8, 20)
        sheet.merge_range('C1:D2', 'General Ledger', title_format1)
        sheet.merge_range('B3:E4', 'Aerospace Baykee Pakistan Private Limited', title_format2)

        sheet.write(row, col, "Nature of Account", header_format)
        sheet.write(row, col + 1, "Analytic Account", header_format)
        sheet.write(row, col + 2, "Analytic Tag ", header_format)
        sheet.write(row, col + 3, "Partner", header_format)
        sheet.write(row, col + 4, "Opening Balance", header_format)
        sheet.write(row, col + 5, "Narration", header_format)
        sheet.write(row, col + 6, "Receipts ", header_format)
        sheet.write(row, col + 7, "Payments", header_format)
        sheet.write(row, col + 8, "Closing Balance", header_format)

        for m in data['main']:
            row += 1
            if not m['account']:
                sheet.write(row, col, "", )
            else:
                sheet.write(row, col, m['partner'], )

            if not m['analytic_account']:
                sheet.write(row, col + 1, "", )
            else:
                sheet.write(row, col + 1, m['analytic_account'], )

            if not m['analytic_tag']:
                sheet.write(row, col + 2, "", )
            else:
                sheet.write(row, col + 2, m['analytic_tag'], )

            if not m['partner']:
                sheet.write(row, col + 3, "", )
            else:
                sheet.write(row, col + 3, m['account'], )

            if not m['open_bal']:
                sheet.write(row, col + 4, "", )
            else:
                sheet.write(row, col + 4, m['open_bal'], )

            if not m['narration']:
                sheet.write(row, col + 5, "", )
            else:
                sheet.write(row, col + 5, m['narration'], )

            if not m['receipt']:
                sheet.write(row, col + 6, "", )
            else:
                sheet.write(row, col + 6, m['receipt'], )

            if not m['payment']:
                sheet.write(row, col + 7, "", )
            else:
                sheet.write(row, col + 7, m['payment'], )

            if not m['close_bal']:
                sheet.write(row, col + 8, "", )
            else:
                sheet.write(row, col + 8, m['close_bal'], )
