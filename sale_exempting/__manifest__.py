{
    'name': 'Sale exempting',
    'version': '17.0',
    'summary': 'Sale exempting',
    'description': 'Sale exempting',
    'category': 'Contact',
    'author': 'Abdelhak',
    'depends': ['account', 'sale_management'],
    'data': [
        'security/exempting_security.xml',
        'security/ir.model.access.csv',
        'data/account_journal_data.xml',
        'data/ir_sequence_data.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/account_invoice_report_views.xml',
        'views/stock_picking_fictitious_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
