# -*- coding: utf-8 -*-
{
    'name': "Inventory Reports Baykee",

    'summary': """
        Customize Inventory Reports""",

    'description': """
        This module customized Stock in hand report
        Add a menu in reporting which name is stock in hand
        open wizard by this menu
        two fields on wizard products and locations
        print report if the fields is selected then it will show the select fields data.
    """,

    'author': "Barak Ullah",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/stock_in_hand_report.xml',
        'wizard/stock_in_hand_wizard.xml',
        'views/views.xml',
    ],
}
