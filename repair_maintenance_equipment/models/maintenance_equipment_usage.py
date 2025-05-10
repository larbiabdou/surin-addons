from odoo import api, fields, models, _


class MaintenanceEquipmentUsage(models.Model):
    _name = 'maintenance.equipment.usage'
    _description = 'Equipment Usage Log'
    _order = 'date desc'

    name = fields.Char(string='Reference', default='/', readonly=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    duration = fields.Float(string='Duration', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
                             default=lambda self: self.env.ref('uom.product_uom_hour'))
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        """Surcharge pour générer un numéro de référence automatique"""
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.equipment.usage') or '/'

        records = super(MaintenanceEquipmentUsage, self).create(vals)
        return records