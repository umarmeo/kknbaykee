# -*- coding: utf-8 -*-
{
    'name': "inventory Reports Baykee",

    'summary': """
        Customize Inventory Reports""",

    'description': """
        This module customized Stock in hand report
        Add a menu in reporting which name is stock in hand
        open wizard by this menu
        two fields on wizard products and locations
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
        'report/pending_delivery_report.xml',
        'report/product_move_report.xml',
        'report/delivery_report.xml',
        'report/dead_stock_report.xml',
        'report/stock_aging_report_template.xml',
        'wizard/stock_in_hand_wizard.xml',
        'wizard/pending_delivery_report_wiz.xml',
        'wizard/product_move_report_wiz.xml',
        'wizard/delivery_report_wiz.xml',
        'wizard/dead_stock_wizard.xml',
        'wizard/stock_aging_report_view.xml',
        'views/views.xml',
    ],
}
