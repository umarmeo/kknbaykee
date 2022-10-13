{
    'name': 'Product Barcode Label Baykee',
    'version': '13.0.1',
    'summary': 'This Module Will Print 4x12 Product Barcode Label',
    'description': 'This Module Will Print 4x12 Product Barcode Label',
    'category': 'Product',
    'author': 'Danish Khalid',
    'website': 'http://www.kknetworks.com.pk',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/product_barcode_label_template.xml',
        'wizard/product_label_view.xml',
        'views/product_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}