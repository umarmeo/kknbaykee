# -*- coding: utf-8 -*-
{
    'name': "Update Account Module Baykee",

    'summary': """
    Customize accounting module
    """,

    'description': """
        - Accounting (acocunt.move) state draft->coo approval->ceo approval->approved->posted with rights
    """,

    'author': "Sayyam Abdul Razzaq",
    'website': "http://www.kknetworks.com.pk",

    # for the full list
    'category': 'accounting',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
    ],
}
