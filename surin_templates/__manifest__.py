{
    'name': 'Surin templates',
    'version': '17.0',
    'summary': 'Surin templates',
    'description': 'Surin templates',
    'category': 'Base',
    'author': 'Abdelhak',
    'depends': ['account_invoice_fixed_discount', 'sale_pdf_quote_builder'],
    'data': [
        'views/external_layout.xml',
        'views/report_invoice_document.xml',
        'views/sale_order_report.xml',
        'views/report_delivery_document.xml',
        'views/report_delivery_fictitious.xml',
        'views/privacy_policy_view.xml',
    ],
    'assets': {
        'web.report_assets_common': [
                'surin_templates/static/src/css/style.css',
            ]
    },
    'installable': True,
    'auto_install': False
}
