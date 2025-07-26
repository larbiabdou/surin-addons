from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Override pour envoyer WhatsApp automatiquement lors de la confirmation"""
        result = super().action_confirm()

        # Envoyer WhatsApp pour les factures clients uniquement
        for sale in self:
                # Appeler la fonction générique d'envoi
            self.env['whatsapp.auto.sender'].send_whatsapp_for_record(
                model_name='sale.order',
                record_id=sale.id
            )

        return result