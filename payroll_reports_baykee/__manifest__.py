# -*- coding: utf-8 -*-
{
    'name': "Payroll Reports Baykee",
    'summary': """
        Customize Payroll Reports""",

    'description': """ """,

    'author': "Danish Khalid",
    'website': "http://www.kknetworks.com.pk",
    'category': 'Payroll',
    'version': '15.0.1',

    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/salary_summary_report.xml',
        'wizards/salary_summary_report_wizard.xml',
        'views/hr_payslip_view.xml',
    ],
}