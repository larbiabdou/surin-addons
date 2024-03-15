from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_real = fields.Boolean(
        string='Is real',
        required=False)    
    
    fictitious_id = fields.Many2one(
        comodel_name='res.partner',
        string='fictitious customer',
        required=False)
