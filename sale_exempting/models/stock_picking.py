from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(readonly=False)

    sale_type = fields.Char(string='Sale Type')

    show_split_button = fields.Boolean(
        string='Show Split Button',
        compute='_compute_show_split_button')

    @api.depends('sale_id', 'sale_id.is_real', 'move_ids')
    def _compute_show_split_button(self):
        for picking in self:
            if picking.sale_id and picking.sale_id.is_real == 'no' and picking.move_ids:
                # Vérifier s'il y a plusieurs types dans ce picking
                sale_types = set()
                for move in picking.move_ids:
                    if move.product_id and move.product_id.sale_type:
                        sale_types.add(move.product_id.sale_type)
                picking.show_split_button = len(sale_types) > 1
            else:
                picking.show_split_button = False

    @api.model
    def create(self, vals):
        return super(StockPicking, self).create(vals)

    # NOUVEAU: Méthode pour séparer le transfert par type de vente
    def action_split_picking(self):
        """Séparer le transfert en plusieurs selon les types de vente"""
        if not self.sale_id or not self.move_ids:
            return

        # Grouper les moves par type de vente
        moves_by_type = {}
        for move in self.move_ids:
            sale_type = move.product_id.sale_type
            if sale_type not in moves_by_type:
                moves_by_type[sale_type] = []
            moves_by_type[sale_type].append(move)

        # Si un seul type, pas besoin de séparer
        if len(moves_by_type) <= 1:
            return

        # Prendre le premier type pour le picking actuel
        sale_types = list(moves_by_type.keys())
        first_type = sale_types[0]
        self.sale_type = first_type

        # Créer de nouveaux pickings pour les autres types
        for sale_type in sale_types[1:]:
            # Créer un nouveau picking
            new_picking_vals = {
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'origin': self.origin,
                'sale_id': self.sale_id.id,
                'sale_type': sale_type,
            }

            new_picking = self.env['stock.picking'].create(new_picking_vals)

            # Transférer les moves existants vers le nouveau picking
            for move in moves_by_type[sale_type]:
                move.write({'picking_id': new_picking.id})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    def button_validate(self):
        # NOUVEAU: Vérification avant validation - séparer automatiquement si nécessaire
        if self.sale_id and self.sale_id.is_real == 'no':
            # Vérifier s'il y a plusieurs types dans ce picking
            sale_types = set()
            for move in self.move_ids:
                if move.product_id and move.product_id.sale_type:
                    sale_types.add(move.product_id.sale_type)

            if len(sale_types) > 1:
                # Séparer automatiquement avant validation
                self.action_split_picking()
                # Après séparation, valider seulement ce picking
                # Les autres seront validés séparément

        super(StockPicking, self).button_validate()

        if self.sale_id:
            # Affecter ce picking comme delivery_id pour la facture
            self.sale_id.delivery_id = self.id

            # Créer une facture pour chaque transfert validé
            payment = self.env['sale.advance.payment.inv'].with_context({
                'active_model': 'sale.order',
                'active_ids': [self.sale_id.id],
                'active_id': self.sale_id.id,
            }).create({
                'advance_payment_method': 'delivered'
            })
            payment.create_invoices()