# -*- coding: utf-8 -*-
{
    'name': "Payment Process Module Baykee",

    'summary': """
        this module can update the payment""",

    'description': """
        -create a name field
        -create a amount field which is Monetary
        -create a purpose field which is text
        -create a state field which is Selection add all the states on form(draft,manager approval,coo approval,
        co approval,approved)
        -Add buttons according to states like manager approval,coo approval,co approval,approve
        -Add cancel buttons
        -Add Reset to draft , Reset to Manager , Reset to coo buttons.
        -Give Access Rights to all buttons.
    """,

    'author': "Barak Ullah",
    'website': "http://www.kknetworks.com.pk",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Amount',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/report_template.xml',
        'security/security.xml',
        'views/views.xml',
        'views/division.xml',
        'views/payment_mode.xml',

    ],

}
