# -*- coding: utf-8 -*-
{
    'name': "Purchase Reports Baykee",

    'summary': """
        This Module can be Create the Report of Purchases""",

    'description': """
    """,

    'author': "KKNetworks",
    'website': "www.kknetworks.com.pk",
    'category': 'Purchase',

    'version': '15.0.1',

    'depends': ['base', 'purchase'],

    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/vendor_price_comparison_template.xml',
        'wizard/vandor_price_comparison_report.xml',
    ],
}
