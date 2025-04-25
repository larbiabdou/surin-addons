# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class PrivacyPolicy(http.Controller):
    @http.route('/privacy-policy', type='http', auth='public', website=True)
    def privacy_policy(self, **kw):
        return request.render('surin_templates.privacy_policy_template', {})