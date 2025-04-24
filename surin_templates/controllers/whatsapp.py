from odoo.http import Controller, route, request

class WhatsAppWebhook(Controller):

    @route('/whatsapp/webhook', auth='public', type='http', csrf=False, methods=['GET', 'POST'])
    def whatsapp_webhook(self, **kwargs):
        if request.httprequest.method == 'GET':
            mode = kwargs.get('hub.mode')
            token = kwargs.get('hub.webhook_verify_token')
            challenge = kwargs.get('hub.challenge')

            # Jeton que TU as défini dans Meta
            VERIFY_TOKEN = 'PAfu1drF'

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return request.make_response(challenge, headers=[('Content-Type', 'text/plain')])
            else:
                return request.make_response("Token invalide", status=403)

        return request.make_response("OK", status=200)