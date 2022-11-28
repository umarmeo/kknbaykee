# -*- coding: utf-8 -*-
{
    'name': "Update Timeoff Form",

    'summary': """
        Leave add into attendance
    """,

    'description': """
        -  Leave add into attendance
    """,

    'author': "Danish Khalid",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Timeoff',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_holidays'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/email_template.xml',
        'views/timeoff_employee.xml',
        'report/report.xml',
        'report/report_template.xml',
        'views/leave_balance_report.xml',
    ],
}
