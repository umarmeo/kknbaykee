# -*- coding: utf-8 -*-
{
    'name': "Payment Process Reports Baykee",
    'summary': """
        Payment Process Reports Baykee""",

    'description': """ Payment Process Reports Baykee """,

    'author': "Danish Khalid",
    'website': "http://www.kknetworks.com.pk",
    'category': 'Payment Process',
    'version': '15.0.1',

    'depends': ['update_payment_process_module_baykee'],
    'data': [
        'security/ir.model.access.csv',
        'reports/reports.xml',
        'reports/payment_status_report_temp.xml',
        'wizards/payment_status_report_wiz.xml',
    ],
}