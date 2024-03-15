{
    'name': 'Sale exempting',
    'version': '17.0',
    'summary': 'Sale exempting',
    'description': 'Sale exempting',
    'category': 'Contact',
    'author': 'Abdelhak',
    'depends': ['account', 'sale_management'],
    'data': [
        'data/account_journal_data.xml',
        'data/ir_sequence_data.xml',
        'security/exempting_security.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
