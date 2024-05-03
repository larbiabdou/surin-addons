from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    stamp_percentage = fields.Float(
        string='Stamp percentage',
        default=1,
        required=False)

    stamp_amount_max = fields.Float(
        string='Stamp amount max',
        default=10000,
        required=False)

    stamp_amount_min = fields.Float(
        string='Stamp amount min',
        default=1,
        required=False)

