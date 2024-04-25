from odoo import api, fields, models


class ResBank(models.Model):
    _inherit = 'res.bank'

    swift = fields.Char(
        string='SWIFT',
        required=False)

