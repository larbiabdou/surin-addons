from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_mode = fields.Selection(
        string='Payment mode',
        selection=[('check', 'Par chèque'),
                   ('virement', 'Virement bancaire'),
                   ('cash', 'Espèce'),
                   ('bank', 'Versement bancaire'),
                   ],
        required=False, )