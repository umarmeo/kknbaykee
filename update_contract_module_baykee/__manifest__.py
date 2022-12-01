# -*- coding: utf-8 -*-
{
    'name': "Update Contract Module Baykee",

    'summary': """
        Contract Module Customizations for Baykee""",

    'description': """
        Contract Module Customizations for Baykee
    """,

    'author': "Danish Khalid",
    'website': "http://www.kknetworks.com.pk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr_contract',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        # 'views/templates.xml',
    ],
}
