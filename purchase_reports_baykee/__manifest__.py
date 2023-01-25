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
        'report/pending_bills_report_template.xml',
        'report/selling_price_variation_template.xml',
        'report/party_wise_purchase_template.xml',
        'report/age_payable_report_template.xml',
        'wizard/vandor_price_comparison_report.xml',
        'wizard/pending_bills_report.xml',
        'wizard/selling_price_variation_report.xml',
        'wizard/party_wise_purchase_report.xml',
        'wizard/age_payable_report.xml',
    ],
}
