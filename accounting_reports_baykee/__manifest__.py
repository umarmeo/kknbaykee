# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports Baykee",

    'summary': """
        This Module can be Create the Report of Accounting""",

    'description': """
    -This module print report of General Entries from this print Menu
    -Taking fields from General Entry and print pdf report from that entries.
    -Add created on (take value for created on from Created_date), Voucher No (take value of voucher no from name field)
     Voucher Date(take value of voucher date from date field) , Status(take value for status from state field , 
     Transaction Amount(take value from transaction amount from amount_total_signed field) in a column.
    -Add a Row with Column Name SR., Account, Partner, Label, Debit, Credit
    -create a serial No for SR. Column, Add account_id field in Account column, Add partner_id field in Partner column,
     Add Label field in Label column, Add Debit field in Debit column, Add Credit field in Credit column
    -Take sum of all debit and credit column values
    -Convert this total amount in words. 
    -Add Remarks heading which value taking from ref field
    """,

    'author': "Sayyam Abdul Razzaq",
    'website': "www.kknetworks.com.pk",
    'category': 'Accounting',

    'version': '15.0.1',

    'depends': ['base', 'account', 'update_account_module_baykee'],

    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/report_template.xml',
        'report/invoice_report_template.xml',
        'report/cash_and_bank_summary_template.xml',
        'report/partner_ledger_report_template.xml',
        'report/general_ledger_report_template.xml',
        'report/baykee_invoice_template.xml',
        'wizard/cash_and_bank_summary.xml',
        'wizard/partner_ledger_report.xml',
        'wizard/general_ledger_report.xml',
    ],
}
