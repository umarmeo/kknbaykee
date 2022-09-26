# -*- coding: utf-8 -*-
{
    'name': "Sale Reports Baykee",

    'summary': """
        This Module can be Create the Report of Sales""",

    'description': """
    """,

    'author': "KKNetworks",
    'website': "www.kknetworks.com.pk",
    'category': 'Sales',

    'version': '15.0.1',

    'depends': ['base', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/item_wise_sale_report_template.xml',
        'report/sale_person_wise_sale_report_template.xml',
        'wizard/item_wise_sale_report.xml',
        'wizard/sale_person_wise_sale_report.xml',
    ],
}
