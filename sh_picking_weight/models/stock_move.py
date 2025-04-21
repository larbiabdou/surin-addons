# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    sh_weight = fields.Float(string="Weight", readonly=True) 


class StockMove(models.Model):
    _inherit = 'stock.move.line'

    sh_weight = fields.Float(string="Weight")

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        print("\n\n\n\n\naggregated_move_lines", aggregated_move_lines)
        for aggregated_move_line in aggregated_move_lines:
            sh_weight = aggregated_move_lines[aggregated_move_line]['product'].weight * \
                aggregated_move_lines[aggregated_move_line]['quantity']
            aggregated_move_lines[aggregated_move_line]['sh_weight'] = sh_weight
        return aggregated_move_lines
