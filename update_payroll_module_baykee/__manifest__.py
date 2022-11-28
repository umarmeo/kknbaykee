{
    'name': 'Update Payroll Module Baykee',
    'version': '15.0.1',
    'summary': 'Payroll Module Baykee',
    'description': 'Payroll Module Baykee',
    'category': 'Payroll',
    'author': 'Danish Khalid',
    'website': 'https://www.kknetworks.com.pk',
    'depends': ['hr_payroll', 'hr', 'hr_work_entry_contract_enterprise', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'wizard/skip_installment.xml',
        'views/advance_loan.xml',
    ],
    'installable': True,
    'auto_install': False,
}