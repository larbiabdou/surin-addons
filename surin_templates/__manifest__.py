{
    'name': 'Surin templates',
    'version': '17.0',
    'summary': 'Surin templates',
    'description': 'Surin templates',
    'category': 'Base',
    'author': 'Abdelhak',
    'depends': ['account_invoice_fixed_discount'],
    'data': [
        'views/external_layout.xml',
        'views/report_invoice_document.xml',
        'views/sale_order_report.xml',
    ],
    'assets': {
        'web.report_assets_common': [
                'surin_templates/static/src/css/style.css',
            ]
    },
    'installable': True,
    'auto_install': False
}
