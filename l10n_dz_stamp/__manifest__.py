{
    'name': 'l10n dz stamp',
    'version': '17.0',
    'summary': 'l10n dz stamp',
    'description': 'Surin l10n dz',
    'category': 'account',
    'author': 'Abdelhak',
    'depends': ['l10n_dz', 'surin_templates'],
    'data': [
        'views/res_config_settings.xml',
        'views/sale_order_views.xml',
        'views/sale_order_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'l10n_dz_stamp/static/src/xml/tax_totals.xml',
        ],
    },
    'installable': True,
    'auto_install': False
}
