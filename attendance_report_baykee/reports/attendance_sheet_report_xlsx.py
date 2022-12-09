from odoo import models, fields, api, _


class AttendanceSheetXlsx(models.AbstractModel):
    _name = 'report.attendance_report_baykee.attendance_sheet_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, main):
        sheet = workbook.add_worksheet('Attendance XLSX Report')
        bold = workbook.add_format({'bold': True})
        title_format1 = workbook.add_format(
            {'bold': True, 'font_color': '#000000', 'bg_color': '#f48531', 'font_size': 14, 'border': 1,
             'align': 'center', 'valign': 'vcenter'})
        title_format2 = workbook.add_format(
            {'bold': True, 'font_color': '#000000', 'bg_color': '#f48531', 'font_size': 10, 'border': 1,
             'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format(
            {'bold': True, 'font_color': '#ffffff', 'bg_color': '#f48531', 'font_size': 9, 'align': 'center', })
        data_style = workbook.add_format(
            {'font_size': 8, 'align': 'center', 'text_wrap': True})

        row = 6
        col = 0
        # data = {'partner_id': partner_id.ids, 'start_date': docs.start_date, 'end_date': docs.end_date}

        sheet.set_column(row, col, 13)
        sheet.set_column(row, col + 1, 13)
        sheet.set_column(row, col + 2, 13)
        if data['type'] == 'emp':
            sheet.merge_range('C1:G2', 'Attendance Sheet Employee Wise', title_format1)
        if data['type'] == 'dpt':
            sheet.merge_range('C1:G2', 'Attendance Sheet Department Wise', title_format1)
        sheet.merge_range('B3:H4', 'Aerospace Baykee Pakistan Private Limited', title_format2)
        sheet.write(row, col, "", header_format)
        sheet.write(row, col + 1, "", header_format)
        sheet.write(row, col + 2, "", header_format)
        sheet.write(row, col + 3, "", header_format)
        for m in data['weekDays']:
            sheet.set_column(row, col + 3, 13)
            sheet.write(row, col + 4, m, header_format)
            col += 1
        sheet.set_column(row, col + 4, 10)
        sheet.set_column(row, col + 5, 10)
        sheet.set_column(row, col + 6, 10)
        sheet.set_column(row, col + 7, 10)
        sheet.set_column(row, col + 8, 10)
        sheet.set_column(row, col + 9, 10)
        sheet.set_column(row, col + 10, 10)
        sheet.write(row, col + 4, "", header_format)
        sheet.write(row, col + 5, "", header_format)
        sheet.write(row, col + 6, "", header_format)
        sheet.write(row, col + 7, "", header_format)
        sheet.write(row, col + 8, "", header_format)
        sheet.write(row, col + 9, "", header_format)
        sheet.write(row, col + 10, "", header_format)
        row += 1
        col = 0
        sheet.write(row, col, "Sr. No", header_format)
        sheet.write(row, col + 1, "Employee", header_format)
        sheet.write(row, col + 2, "Designation", header_format)
        sheet.write(row, col + 3, "Department", header_format)
        for t in data['total_days']:
            sheet.write(row, col + 4, t, header_format)
            col += 1
        sheet.write(row, col + 4, "Total Days", header_format)
        sheet.write(row, col + 5, "Absent Days", header_format)
        sheet.write(row, col + 6, "Late Days", header_format)
        sheet.write(row, col + 7, "Leave Days", header_format)
        sheet.write(row, col + 8, "Short Leaves", header_format)
        sheet.write(row, col + 9, "Half Leaves", header_format)
        sheet.write(row, col + 10, "Present Days", header_format)
        row += 1
        col = 0
        sr = 1
        for ma in data['main']:
            sheet.write(row, col, sr, data_style)
            sheet.write(row, col + 1, ma['employee'], data_style)
            sheet.write(row, col + 2, ma['design'], data_style)
            sheet.write(row, col + 3, ma['dept'], data_style)
            for att in ma['days']:
                sheet.write(row, col + 4, att, data_style)
                col += 1
            col = ma['total_no_days']
            sheet.write(row, col + 4, ma['total_no_days'], data_style)
            sheet.write(row, col + 5, ma['total_absent'], data_style)
            sheet.write(row, col + 6, ma['total_late'], data_style)
            sheet.write(row, col + 7, ma['total_leave'], data_style)
            sheet.write(row, col + 8, ma['total_short'], data_style)
            sheet.write(row, col + 9, ma['total_half'], data_style)
            sheet.write(row, col + 10, ma['total_present'], data_style)
            row += 1
            col = 0
            sr += 1
