# -*- coding: utf-8 -*-
{
    'name': "Update Employee Module",

    'summary': """
        Update Employee Module""",

    'description': """
        Update Employee Module
    """,

    'author': "Muhammad Awais Ather",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Employee',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
