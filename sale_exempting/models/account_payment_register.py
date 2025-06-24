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

    payment_mode = fields.Selection(
        string='Payment mode',
        selection=[('check', 'Par chèque'),
                   ('virement', 'Virement bancaire'),
                   ('cash', 'Espèce'),
                   ('bank', 'Versement bancaire'),
                   ],
        compute="compute_payment_mode",
        store=True,
        required=False)

    check_number = fields.Char(string='Numéro de chèque')
    virement_number = fields.Char(string='Numéro de virement')
    versement_number = fields.Char(string='Numéro de versement')

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

    @api.depends('line_ids')
    def compute_payment_mode(self):
        ''' Load payment_mode from the account.moves passed through the context. '''
        for wizard in self:
            batches = wizard._get_batches()
            batch_result = batches[0]
            lines = batch_result['lines']
            if lines:
                wizard.payment_mode = lines[0].move_id.payment_mode
            else:
                wizard.payment_mode = False

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        payment_vals['is_real'] = self.is_real
        payment_vals['is_fictitious'] = self.is_fictitious
        payment_vals['is_invisible'] = True
        payment_vals['payment_mode'] = self.payment_mode
        payment_vals['check_number'] = self.check_number
        payment_vals['virement_number'] = self.virement_number
        payment_vals['versement_number'] = self.versement_number
        payment_vals['payment_mode'] = self.payment_mode
        return payment_vals