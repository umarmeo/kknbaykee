# -*- coding: utf-8 -*-
{
    'name': "Update Contact Module Baykee",

    'summary': """
        Contact Module Customizations for Baykee""",

    'description': """
        Contact Module Customizations for Baykee
    """,

    'author': "Danish Khalid",
    'website': "http://www.kknetworks.com.pk",

    'category': 'Contacts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts'],

    # always loaded
    'data': [
        'views/res_partner_view.xml',
    ],
}
