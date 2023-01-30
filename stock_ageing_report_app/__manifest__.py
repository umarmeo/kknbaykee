{
    'name': 'Inventory and Stock Aging Report for Warehouse Baykee',
    'author': "Edge Technologies",
    'version': '15.0.1.1',
    "images": ["static/description/main_screenshot.png"],
    'summary': 'Product stock aging reports inventory aging report warehouse aging report product aging report for stock expiry report inventory expiry report stock overdue stock report due stock report product due report stock overdate report overdate stock reports.',
    'description': """
        Stock inventory aging report filter by product, category, location, warehouse, date, and period length.
    """,
    'depends': ['base', 'sale_management', 'stock'],
    "license": "OPL-1",
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_aging_report_view.xml',
        'report/stock_aging_report.xml',
        'report/stock_aging_report_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'category': 'Warehouse',
}
