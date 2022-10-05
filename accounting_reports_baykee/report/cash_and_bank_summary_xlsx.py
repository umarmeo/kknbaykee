from odoo import models


class CashAndBankSummaryXlsx(models.AbstractModel):
    _name = 'report.accounting_reports_baykee.cash_bank_summary_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, main):
        sheet = workbook.add_worksheet('Bank and Cash Summary XLSX Report')
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
        # data = {'partner_id': partner_id.ids, 'start_date': docs.start_date, 'end_date': docs.end_date}
        fold = data['form']['fold']

        sheet.set_column(row, col, 20)
        sheet.set_column(row, col + 1, 20)
        sheet.set_column(row, col + 2, 20)
        sheet.set_column(row, col + 3, 20)
        sheet.set_column(row, col + 4, 20)
        sheet.set_column(row, col + 5, 20)
        sheet.merge_range('C1:D2', 'Cash and Bank Summary', title_format1)
        sheet.merge_range('B3:E4', 'Aerospace Baykee Pakistan Private Limited', title_format2)
        # sheet.write(0, 2, 'Cash and Bank Summary', title_format)
        if fold == '0':
            sheet.write(row, col, "Nature of Account", header_format)
            sheet.write(row, col + 1, "Opening Balance", header_format)
            sheet.write(row, col + 2, "Receipts ", header_format)
            sheet.write(row, col + 3, "Payments", header_format)
            sheet.write(row, col + 4, "Closing Balance", header_format)
            receipt = 0
            payment = 0
            open_bal = 0
            close_bal = 0
            for m in data['main']:
                open_bal += m['open_bal']
                receipt += m['receipt']
                payment += m['payment']
                close_bal = open_bal + receipt - payment
                row += 1
                if not m['account']:
                    sheet.write(row, col, "", )
                else:
                    sheet.write(row, col, m['account'], )

                if not m['open_bal']:
                    sheet.write(row, col + 1, "", )
                else:
                    sheet.write(row, col + 1, m['open_bal'], )

                if not m['receipt']:
                    sheet.write(row, col + 2, "", )
                else:
                    sheet.write(row, col + 2, m['receipt'], )

                if not m['payment']:
                    sheet.write(row, col + 3, "", )
                else:
                    sheet.write(row, col + 3, m['payment'], )

                if not m['close_bal']:
                    sheet.write(row, col + 4, "", )
                else:
                    sheet.write(row, col + 4, m['close_bal'], )
            sheet.write(row + 1, col, "Total", header_format)
            sheet.write(row + 1, col + 1, open_bal, header_format)
            sheet.write(row + 1, col + 2, receipt, header_format)
            sheet.write(row + 1, col + 3, payment, header_format)
            sheet.write(row + 1, col + 4, close_bal, header_format)

        if fold == '1':
            sheet.write(row, col, "Nature of Account", header_format)
            sheet.write(row, col + 1, "Opening Balance", header_format)
            sheet.write(row, col + 2, "Narration", header_format)
            sheet.write(row, col + 3, "Receipts ", header_format)
            sheet.write(row, col + 4, "Payments", header_format)
            sheet.write(row, col + 5, "Closing Balance", header_format)
            receipt = 0
            payment = 0
            open_bal = 0
            close_bal = 0
            for m in data['main']:
                open_bal += m['open_bal']
                receipt += m['receipt']
                payment += m['payment']
                close_bal = open_bal + receipt - payment
                row += 1
                if not m['account']:
                    sheet.write(row, col, "", )
                else:
                    sheet.write(row, col, m['account'], )

                if not m['open_bal']:
                    sheet.write(row, col + 1, "", )
                else:
                    sheet.write(row, col + 1, m['open_bal'], )

                if not m['narration']:
                    sheet.write(row, col + 2, "", )
                else:
                    sheet.write(row, col + 2, m['narration'],)

                if not m['receipt']:
                    sheet.write(row, col + 3, "", )
                else:
                    sheet.write(row, col + 3, m['receipt'], )

                if not m['payment']:
                    sheet.write(row, col + 4, "", )
                else:
                    sheet.write(row, col + 4, m['payment'], )

                if not m['close_bal']:
                    sheet.write(row, col + 5, "", )
                else:
                    sheet.write(row, col + 5, m['close_bal'], )

            sheet.write(row + 1, col, "Total", header_format)
            sheet.write(row + 1, col + 1, open_bal, header_format)
            sheet.write(row + 1, col + 2, "", header_format)
            sheet.write(row + 1, col + 3, receipt, header_format)
            sheet.write(row + 1, col + 4, payment, header_format)
            sheet.write(row + 1, col + 5, close_bal, header_format)
