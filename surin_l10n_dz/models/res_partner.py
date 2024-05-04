from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rc = fields.Char(
        string='RC',
        required=False)
    nif = fields.Char(
        string='NIF',
        required=False)
    ai = fields.Char(
        string='AI',
        required=False)
    nis = fields.Char(
        string='NIS',
        required=False)
    legal_status = fields.Selection(
        string='Legal status',
        selection=[('sarl', 'SARL'),
                   ('eurl', 'EURL'),
                   ('spa', 'SPA'),
                   ('snc', 'SNC'),
                   ('etablissement', 'Établissement'),
                   ('ets', 'ETS'),
                   ],
        required=False, )
        