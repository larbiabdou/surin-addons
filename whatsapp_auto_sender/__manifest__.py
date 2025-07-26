
# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Auto Sender',
    'version': '17.0.1.0.0',
    'summary': 'Envoi automatique de messages WhatsApp',
    'description': """
Module pour l'envoi automatique de messages WhatsApp lors d'événements spécifiques.
- Envoi automatique lors de la confirmation de facture
- Utilise le composer WhatsApp standard d'Odoo
- Fonction générique réutilisable
    """,
    'author': 'Votre Nom',
    'category': 'Communication',
    'depends': ['base', 'whatsapp', 'account', 'sale_exempting'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}