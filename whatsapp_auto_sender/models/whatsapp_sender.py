from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class WhatsAppAutoSender(models.AbstractModel):
    """Service pour l'envoi automatique de messages WhatsApp"""
    _name = 'whatsapp.auto.sender'
    _description = 'WhatsApp Auto Sender Service'

    @api.model
    def send_whatsapp_for_record(self, model_name, record_id, template_external_id=None):
        """
        Fonction générique pour envoyer un message WhatsApp automatiquement

        :param model_name: Nom du modèle (ex: 'account.move')
        :param record_id: ID de l'enregistrement
        :param template_external_id: ID externe du template (optionnel)
        :return: Messages WhatsApp créés ou False
        """
        try:
            # Récupérer l'enregistrement
            record = self.env[model_name].browse(record_id)
            if not record.exists():
                _logger.warning(f"Enregistrement {model_name}[{record_id}] non trouvé")
                return False

            # Chercher le template approprié
            template = self._find_template_for_model(model_name, template_external_id)
            if not template:
                _logger.warning(f"Aucun template WhatsApp trouvé pour le modèle {model_name}")
                return False

            # Vérifier si le numéro de téléphone existe
            if not self._has_valid_phone(record, template):
                _logger.info(f"Pas de numéro de téléphone valide pour {model_name}[{record_id}]")
                return False

            # Créer et envoyer via composer
            return self._create_and_send_composer(record, template)

        except Exception as e:
            _logger.error(f"Erreur lors de l'envoi WhatsApp pour {model_name}[{record_id}]: {str(e)}")
            return False

    def _find_template_for_model(self, model_name, template_external_id=None):
        """Trouve le template WhatsApp approprié pour le modèle"""
        Template = self.env['whatsapp.template']

        # Si un template spécifique est demandé via external_id
        if template_external_id:
            try:
                template = self.env.ref(template_external_id, raise_if_not_found=False)
                if template and template.status == 'approved':
                    return template
            except Exception:
                _logger.warning(f"Template {template_external_id} non trouvé ou non approuvé")

        # Chercher par model_id
        model = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
        if not model:
            return False

        templates = Template.search([
            ('model_id', '=', model.id),
            ('status', '=', 'approved'),
        ], limit=1)

        return templates[0] if templates else False

    def _has_valid_phone(self, record, template):
        """Vérifie si l'enregistrement a un numéro de téléphone valide"""
        if not template.phone_field:
            return False

        try:
            phone_value = record._find_value_from_field_path(template.phone_field)
            return bool(phone_value and str(phone_value).strip())
        except Exception:
            return False

    def _create_and_send_composer(self, record, template):
        """Crée le composer WhatsApp et envoie le message"""
        try:
            # Préparer le contexte pour le composer
            context = {
                'active_model': record._name,
                'active_id': record.id,
                'active_ids': [record.id],
            }

            # Créer le composer avec les valeurs requises
            composer_vals = {
                'res_model': record._name,
                'res_ids': str([record.id]),
                'wa_template_id': template.id,
                'batch_mode': False,
            }

            # Créer le composer
            composer = self.env['whatsapp.composer'].with_context(**context).create(composer_vals)

            # Envoyer le message via la méthode standard
            messages = composer._send_whatsapp_template(force_send_by_cron=True)

            if messages:
                _logger.info(f"Message WhatsApp envoyé avec succès pour {record._name}[{record.id}]")
                return messages
            else:
                _logger.warning(f"Échec de l'envoi WhatsApp pour {record._name}[{record.id}]")
                return False

        except Exception as e:
            _logger.error(f"Erreur lors de la création du composer WhatsApp: {str(e)}")
            return False