# -*- coding: utf-8 -*-
{
    'name': "Update Sale Module Baykee",

    'summary': """
    Customize sale module
    """,

    'description': """
        -  Remove create and edit button from every field
    """,

    'author': "Sayyam Abdul Razzaq",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
