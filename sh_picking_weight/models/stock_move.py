# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    sh_weight = fields.Float(string="Weight", readonly=True, digits=(16, 2))


class StockMove(models.Model):
    _inherit = 'stock.move.line'

    sh_weight = fields.Float(string="Weight", digits=(16, 2))

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        print("\n\n\n\n\naggregated_move_lines", aggregated_move_lines)
        for aggregated_move_line in aggregated_move_lines:
            sh_weight = aggregated_move_lines[aggregated_move_line]['product'].weight * \
                        aggregated_move_lines[aggregated_move_line]['quantity']
            # Arrondir à deux chiffres après la virgule
            aggregated_move_lines[aggregated_move_line]['sh_weight'] = round(sh_weight, 2)
        return aggregated_move_lines
