from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sh_total_weight = fields.Float(string="Total Weight", compute="_compute_sh_total_weight")
    sh_line_total_weight = fields.Float(
        string="Total Weight", compute="_compute_sh_line_total_weight")


    def _compute_sh_total_weight(self):
        for rec in self:
            rec.sh_total_weight = 0
            total = 0
            for res in rec.move_ids_without_package:
                print("\n\n\n\n\Res", res.product_id)
                temp = res.product_uom_qty * res.product_id.weight
                res.sh_weight = temp
                total += res.sh_weight
            rec.sh_total_weight = total

    def _compute_sh_line_total_weight(self):
        for rec in self:
            rec.sh_line_total_weight = 0
            line_total = 0
            for line in rec.move_line_ids_without_package:
                temp_line = line.quantity * line.product_id.weight
                line.sh_weight = temp_line
                line_total += line.sh_weight
                rec.sh_line_total_weight = line_total




