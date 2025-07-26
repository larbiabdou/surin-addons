from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Override pour envoyer WhatsApp automatiquement lors de la confirmation"""
        result = super().action_post()

        # Envoyer WhatsApp pour les factures clients uniquement
        for move in self:
            if move.move_type in ['out_invoice'] and move.is_real:
                # Appeler la fonction générique d'envoi
                self.env['whatsapp.auto.sender'].send_whatsapp_for_record(
                    model_name='account.move',
                    record_id=move.id
                )

        return result