# -*- coding: utf-8 -*-
{
    'name': "Update Inventory Module Baykee",

    'summary': """
    Customize Compete Inventory module
    """,

    'description': """
        -  Customize delivery slip report
        -  Customize picking operation report 
        -  Remove create and edit button from every field
    """,

    'author': "Sayyam Abdul Razzaq",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'inventory',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/delivery_slip_report.xml',
        'report/picking_operation_report.xml',
        'views/views.xml',
        'views/product_label_layout.xml',
    ],
}
