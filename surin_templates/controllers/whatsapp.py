from odoo.http import Controller, route, request
import logging
_logger = logging.getLogger(__name__)

class WhatsAppWebhook(Controller):

    @route('/whatsapp/webhook', auth='public', type='http', csrf=False, methods=['GET', 'POST'])
    def whatsapp_webhook(self, **kwargs):
        if request.httprequest.method == 'GET':
            mode = kwargs.get('hub.mode')
            token = kwargs.get('hub.verify_token')
            challenge = kwargs.get('hub.challenge')
            _logger.info("enter")
            # Jeton que TU as défini dans Meta
            VERIFY_TOKEN = 'PAfu1drF'
            _logger.info(token)
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                _logger.info(token)
                return request.make_response(challenge, headers=[('Content-Type', 'text/plain')])
            else:
                return request.make_response("Token invalide", status=403)

        return request.make_response("OK", status=200)