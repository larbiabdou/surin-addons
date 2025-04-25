# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class PrivacyPolicy(http.Controller):
    @http.route('/privacy-policy', type='http', auth='public', website=True)
    def privacy_policy(self, **kw):
        html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Politique de Confidentialité</title>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            </head>
            <body>
                <h1>Politique de Confidentialité</h1>
                <p>Nous respectons la vie privée de nos utilisateurs. Toutes les données échangées via WhatsApp sont utilisées uniquement pour fournir des services via notre système ERP (Odoo) et ne sont ni revendues ni partagées.</p>
                <p>Pour toute question, veuillez nous contacter à marketing@surin-dz.com.</p>
            </body>
            </html>
            """
        return html_content