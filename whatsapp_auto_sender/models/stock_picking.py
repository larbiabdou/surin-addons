from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """Override pour envoyer WhatsApp automatiquement lors de la confirmation"""
        super(StockPicking, self).button_validate()

        # Envoyer WhatsApp pour les factures clients uniquement
        for picking in self:
                # Appeler la fonction générique d'envoi
            if picking.picking_type_id.code == 'outgoing':
                self.env['whatsapp.auto.sender'].send_whatsapp_for_record(
                    model_name='stock.picking',
                    record_id=picking.id
                )