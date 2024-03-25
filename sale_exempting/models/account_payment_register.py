# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_real = fields.Boolean(
        string='Is real',
        compute="compute_payment_type",
        store=True,
        required=False)

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        compute="compute_payment_type",
        store=True,
        required=False)

    @api.depends('line_ids')
    def compute_payment_type(self):
        ''' Load initial values from the account.moves passed through the context. '''
        for wizard in self:
            batches = wizard._get_batches()
            batch_result = batches[0]
            lines = batch_result['lines']
            if lines:
                wizard.is_real = lines[0].is_real
                wizard.is_fictitious = lines[0].is_fictitious

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        payment_vals['is_real'] = self.is_real
        payment_vals['is_fictitious'] = self.is_fictitious
        return payment_vals
