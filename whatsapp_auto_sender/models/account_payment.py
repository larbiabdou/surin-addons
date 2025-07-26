from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        """Override pour envoyer WhatsApp automatiquement lors de la confirmation"""
        result = super().action_post()

        # Envoyer WhatsApp pour les factures clients uniquement
        for payment in self:
                # Appeler la fonction générique d'envoi
            self.env['whatsapp.auto.sender'].send_whatsapp_for_record(
                model_name='account.payment',
                record_id=payment.id
            )

        return result