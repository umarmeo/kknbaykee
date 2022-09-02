# -*- coding: utf-8 -*-
{
    'name': "Update Purchase Module Baykee",

    'summary': """
        Customize purchase module""",

    'description': """
        -  Remove create and edit button from every field
    """,

    'author': "Sayyam Abdul Razzaq",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'purchase',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        # 'views/purchase_report.xml',
    ],
}
