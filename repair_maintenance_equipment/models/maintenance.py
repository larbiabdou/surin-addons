from odoo import api, fields, models, _


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    repair_order_ids = fields.One2many('repair.order', 'maintenance_request_id',
                                       string='Repair Orders')
    repair_count = fields.Integer(compute='_compute_repair_count', string='Repair Count')

    @api.depends('repair_order_ids')
    def _compute_repair_count(self):
        """Calculer le nombre de réparations liées"""
        for request in self:
            request.repair_count = len(request.repair_order_ids)

    def action_create_repair(self):
        """Action pour créer une nouvelle réparation"""
        self.ensure_one()

        return {
            'name': _('Create Repair Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'repair.order',
            'view_mode': 'form',
            'context': {
                'default_maintenance_request_id': self.id,
                'default_equipment_id': self.equipment_id.id if self.equipment_id else False,
            },
            'target': 'current',
        }

    def action_view_repairs(self):
        """Action pour afficher les réparations liées"""
        self.ensure_one()

        return {
            'name': _('Repair Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'repair.order',
            'view_mode': 'tree,form',
            'domain': [('maintenance_request_id', '=', self.id)],
            'context': {
                'default_maintenance_request_id': self.id,
                'default_equipment_id': self.equipment_id.id if self.equipment_id else False,
            },
        }