from odoo import api, fields, models, tools


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    import_folder_id = fields.Many2one(
        comodel_name='import.folder',
        string='Import_folder_id',
        required=False)

    def button_validate(self):
        res = super().button_validate()
        for record in self:
            if record.import_folder_id:
                record.import_folder_id.compute_landed_cost_matrix()
        return res

    def button_reset_to_draft(self):
        for record in self:
            record.state = 'draft'
            if record.account_move_id:
                record.account_move_id.button_draft()
                record.account_move_id = False
                record.account_move_id.unlink()



    def _get_targeted_move_ids(self):
        return self.picking_ids.move_ids.filtered(lambda l: l.product_id.gender != 'male')

    selective_cost_application = fields.Boolean(
        string='Appliqué par séléction',
        default=False,
        help="Enable selective application of costs to specific products"
    )

    def compute_landed_cost(self):
        """Override pour application sélective des coûts"""
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            cost = cost.with_company(cost.company_id)
            rounding = cost.currency_id.rounding
            all_val_line_values = cost.get_valuation_lines()

            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    # MODIFICATION: Vérifier si l'application sélective est activée
                    if cost.selective_cost_application and cost_line.product_ids:
                        # Si des produits spécifiques sont sélectionnés, vérifier si le produit courant y est
                        if val_line_values.get('product_id') not in cost_line.product_ids.ids:
                            continue  # Ignorer ce produit pour cette ligne de coût

                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)

            # Calcul des coûts pour chaque ligne de coût
            for line in cost.cost_lines:
                value_split = 0.0

                # Obtenir les lignes de valorisation pertinentes pour cette ligne de coût
                relevant_valuations = cost.valuation_adjustment_lines.filtered(
                    lambda v: v.cost_line_id and v.cost_line_id.id == line.id
                )

                if not relevant_valuations:
                    continue

                # Calculer les totaux pour cette ligne de coût spécifique
                line_total_qty = sum(relevant_valuations.mapped('quantity'))
                line_total_weight = sum(relevant_valuations.mapped('weight'))
                line_total_volume = sum(relevant_valuations.mapped('volume'))
                line_total_cost = sum(relevant_valuations.mapped('former_cost'))
                line_total_line = len(relevant_valuations)

                for valuation in relevant_valuations:
                    value = 0.0
                    if line.split_method == 'by_quantity' and line_total_qty:
                        per_unit = (line.price_unit / line_total_qty)
                        value = valuation.quantity * per_unit
                    elif line.split_method == 'by_weight' and line_total_weight:
                        per_unit = (line.price_unit / line_total_weight)
                        value = valuation.weight * per_unit
                    elif line.split_method == 'by_volume' and line_total_volume:
                        per_unit = (line.price_unit / line_total_volume)
                        value = valuation.volume * per_unit
                    elif line.split_method == 'equal':
                        value = (line.price_unit / line_total_line) if line_total_line else 0
                    elif line.split_method == 'by_current_cost_price' and line_total_cost:
                        per_unit = (line.price_unit / line_total_cost)
                        value = valuation.former_cost * per_unit
                    else:
                        value = (line.price_unit / line_total_line) if line_total_line else 0

                    if rounding:
                        value = tools.float_round(value, precision_rounding=rounding, rounding_method='HALF-UP')
                        value_split += value

                    if valuation.id not in towrite_dict:
                        towrite_dict[valuation.id] = value
                    else:
                        towrite_dict[valuation.id] += value

                # Gérer les différences d'arrondi
                rounding_diff = cost.currency_id.round(line.price_unit - value_split)
                if not cost.currency_id.is_zero(rounding_diff) and relevant_valuations:
                    max_valuation_id = max(v.id for v in relevant_valuations)
                    if max_valuation_id in towrite_dict:
                        towrite_dict[max_valuation_id] += rounding_diff

        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    product_ids = fields.Many2many(
        'product.product',
        string='Appliqué sur',
        help="Select specific products to apply this cost. Leave empty to apply to all products."
    )

    @api.depends('cost_id.picking_ids')
    def _compute_available_products_domain(self):
        """Compute domain for available products based on pickings"""
        for line in self:
            line.available_products_domain = False
            if line.cost_id and line.cost_id.picking_ids:
                # Récupérer tous les produits des mouvements de stock des pickings
                # avec le même filtre que _get_targeted_move_ids
                move_ids = line.cost_id.picking_ids.move_ids
                product_ids = move_ids.mapped('product_id').ids
                line.available_products_domain = product_ids

    available_products_domain = fields.Many2many('product.product',
        compute='_compute_available_products_domain',
        store=False
    )
