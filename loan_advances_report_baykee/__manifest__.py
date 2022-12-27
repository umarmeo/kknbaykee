# -*- coding: utf-8 -*-
{
    'name': "Loan Advances Reports Baykee",

    'summary': """
    This Module can be Create the Report of Loan and Advance""",

    'description': """
    This Module can be Create the Report of Loan and Advance
    """,

    'author': "Danish Khalid",
    'website': "www.kknetworks.com.pk",
    'category': 'Loan',

    'version': '15.0.1',

    'depends': ['base', 'account', 'update_payroll_module_baykee'],

    'data': [
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/advance_loan_application_form_report.xml',
        'wizards/employee_advance_report.xml',
        'reports/employee_advance_salary_temp.xml',
        'reports/employee_loan_temp.xml',
        'wizards/employee_loan_report.xml',
    ],
}
