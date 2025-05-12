from odoo import api, fields, models,_


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    last_maintenance_hours = fields.Float(string='Last Maintenance Hours', readonly=True,
                                          help='Last recorded threshold hours from repair orders')

    duration_of_use = fields.Float(string='Duration of Use', compute='_compute_duration_of_use', store=True,
                                   help='Last recorded duration of use')

    usage_log_ids = fields.One2many('maintenance.equipment.usage', 'equipment_id', string='Usage Logs')
    usage_log_count = fields.Integer(compute='_compute_usage_log_count', string='Usage Count')

    repair_order_ids = fields.One2many('repair.order', 'equipment_id',
                                       string='Repair Orders')
    repair_count = fields.Integer(compute='_compute_repair_count', string='Repair Count')

    @api.depends('repair_order_ids')
    def _compute_repair_count(self):
        """Calculer le nombre de réparations liées"""
        for request in self:
            request.repair_count = len(request.repair_order_ids)

    def action_view_repairs(self):
        """Action pour afficher les réparations liées"""
        self.ensure_one()

        return {
            'name': _('Repair Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'repair.order',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {
                'default_equipment_id': self.id,
            },
        }
    @api.depends('usage_log_ids', 'usage_log_ids.date', 'usage_log_ids.duration')
    def _compute_duration_of_use(self):
        """Calculer la dernière durée d'utilisation enregistrée avec la plus grande durée"""
        for equipment in self:
            # Récupérer les enregistrements du jour le plus récent
            last_date_usage = self.env['maintenance.equipment.usage'].search(
                [('equipment_id', '=', equipment.id)],
                order='date desc', limit=1)

            if not last_date_usage:
                equipment.duration_of_use = 0.0
                continue

            last_date = last_date_usage.date

            # Trouver l'enregistrement avec la plus grande durée à cette date
            max_duration_usage = self.env['maintenance.equipment.usage'].search(
                [('equipment_id', '=', equipment.id), ('date', '=', last_date)],
                order='duration desc', limit=1)

            equipment.duration_of_use = max_duration_usage.duration if max_duration_usage else 0.0

    @api.depends('usage_log_ids')
    def _compute_usage_log_count(self):
        """Calculer le nombre d'enregistrements d'utilisation"""
        for equipment in self:
            equipment.usage_log_count = len(equipment.usage_log_ids)

    def action_view_usage_logs(self):
        """Action pour voir les journaux d'utilisation"""
        self.ensure_one()

        return {
            'name': _('Usage Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.equipment.usage',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

    def action_record_usage(self):
        """Action pour enregistrer une nouvelle utilisation"""
        self.ensure_one()

        return {
            'name': _('Record Equipment Usage'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.equipment.usage',
            'view_mode': 'form',
            'context': {
                'default_equipment_id': self.id,
                'default_date': fields.Date.today(),
            },
            'target': 'new',
        }