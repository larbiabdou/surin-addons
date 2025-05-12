# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    # Ajout du champ Last Threshold Hours
    last_threshold_hours = fields.Float(string='Last Threshold Hours')

    # Nouveau champ pour lier à maintenance.equipment
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')

    # Relation avec les demandes de maintenance
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')

    def action_repair_done(self):
        """Surcharge de la méthode pour mettre à jour la demande de maintenance"""
        res = super(RepairOrder, self).action_repair_done()

        # Mettre l'état de la demande de maintenance à "terminé" si elle existe
        if self.maintenance_request_id:
            self.maintenance_request_id.stage_id = self.env.ref('maintenance.stage_3')
            # Mettre à jour les valeurs de l'équipement
        if self.equipment_id and self.last_threshold_hours:
            self.equipment_id.last_maintenance_hours = self.last_threshold_hours

        return res

    def action_validate(self):
        # Appel à la méthode originale
        res = super(RepairOrder, self).action_validate()

        # Création de l'enregistrement d'usage d'équipement
        for repair in self:
            if repair.equipment_id and repair.last_threshold_hours:
                self.env['maintenance.equipment.usage'].create({
                    'equipment_id': repair.equipment_id.id,
                    'date': fields.Date.today(),
                    'duration': repair.last_threshold_hours,
                    'notes': _("Created from repair order: %s") % repair.name,
                })

        return res