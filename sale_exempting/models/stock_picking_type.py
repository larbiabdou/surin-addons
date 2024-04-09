from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_real = fields.Boolean(
        string='Is real',
        required=False)
