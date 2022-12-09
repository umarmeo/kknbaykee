# -*- coding: utf-8 -*-
{
    'name': "Attendance Reports Baykee",
    'summary': """
        Customize Attendance Reports""",

    'description': """ """,

    'author': "Danish Khalid",
    'website': "http://www.kknetworks.com.pk",
    'category': 'Attendance',
    'version': '15.0.1',

    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report.xml',
        'wizards/attendance_sheet_report_wizard.xml',
    ],
}