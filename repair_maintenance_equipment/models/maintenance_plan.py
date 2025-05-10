# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class MaintenancePlan(models.Model):
    _name = 'maintenance.plan'
    _description = 'Maintenance Plan'

    name = fields.Char(string='Code', default=lambda self: _('New'), readonly=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True)

    maintenance_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive')
    ], string='Type of Maintenance', default='preventive', required=True)

    plan_type = fields.Selection([
        ('periodic', 'Periodic'),
        ('usage', 'Usage')
    ], string='Type', required=True, default='periodic')

    interval_value = fields.Integer(string='Interval Value',
                                    help="Value of the interval for periodic maintenance.")
    interval_unit = fields.Selection([
        ('day', 'Day'),
        ('month', 'Month'),
        ('year', 'Year')
    ], string='Interval Unit', default='month')

    usage_threshold = fields.Integer(string='Usage Threshold (Hours)',
                                     help="Number of hours for usage-based maintenance")

    last_triggered_date = fields.Date(string='Last Triggered Date')
    last_triggered_hours = fields.Integer(string='Last Triggered Hours')

    necessary_part_ids = fields.One2many('maintenance.plan.part', 'plan_id', string='Necessary Parts')

    anticipation_hours = fields.Integer(string='Anticipation Hours')

    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                year = datetime.now().strftime('%y')
                sequence = self.env['ir.sequence'].next_by_code('maintenance.plan') or '001'
                vals['name'] = sequence
        return super(MaintenancePlan, self).create(vals_list)

    @api.depends('necessary_part_ids.total')
    def _compute_total_cost(self):
        for plan in self:
            plan.total_cost = sum(plan.necessary_part_ids.mapped('total'))

    def _cron_generate_maintenance_requests(self):
        """
        Cron job to automatically generate maintenance requests
        based on plan configuration
        """
        today = fields.Date.today()

        # Process periodic plans
        periodic_plans = self.search([
            ('plan_type', '=', 'periodic'),
            ('active', '=', True)
        ])

        for plan in periodic_plans:
            if not plan.last_triggered_date:
                self._create_maintenance_request(plan)
                continue

            next_date = plan.last_triggered_date
            if plan.interval_unit == 'day':
                next_date += relativedelta(days=plan.interval_value)
            elif plan.interval_unit == 'month':
                next_date += relativedelta(months=plan.interval_value)
            elif plan.interval_unit == 'year':
                next_date += relativedelta(years=plan.interval_value)

            if next_date <= today:
                self._create_maintenance_request(plan)

        # Process usage-based plans
        usage_plans = self.search([
            ('plan_type', '=', 'usage'),
            ('active', '=', True)
        ])

        for plan in usage_plans:
            current_hours = plan.equipment_id.duration_of_use or 0
            last_hours = plan.last_triggered_hours or 0

            if current_hours - last_hours >= plan.usage_threshold:
                self._create_maintenance_request(plan)

    def _create_maintenance_request(self, plan):
        """Create repair order based on maintenance plan"""
        RepairOrder = self.env['repair.order']
        StockMove = self.env['stock.move']

        repair_vals = {
            'equipment_id': plan.equipment_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'company_id': plan.company_id.id,
            'last_threshold_hours': plan.equipment_id.duration_of_use,
            'state': 'draft',
        }

        # Create repair order
        repair = RepairOrder.create(repair_vals)

        # Add necessary parts as stock moves
        for part in plan.necessary_part_ids:
            StockMove.create({
                'repair_id': repair.id,
                'name': part.product_id.display_name,
                'product_id': part.product_id.id,
                'product_uom_qty': part.quantity,
                'product_uom': part.uom_id.id,
                'repair_line_type': 'add',
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'company_id': plan.company_id.id,
                'state': 'draft',
            })

        # Update plan with last triggered info
        plan.write({
            'last_triggered_date': fields.Date.today(),
            'last_triggered_hours': plan.equipment_id.duration_of_use or 0
        })

        return repair


# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MaintenancePlanPart(models.Model):
    _name = 'maintenance.plan.part'
    _description = 'Maintenance Plan Part'

    plan_id = fields.Many2one('maintenance.plan', string='Maintenance Plan', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 domain=[('type', 'in', ['product', 'consu'])])
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                             domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    cost = fields.Float(string='Unit Cost', compute='_compute_cost', store=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    @api.depends('product_id')
    def _compute_cost(self):
        for record in self:
            record.cost = record.product_id.standard_price

    @api.depends('quantity', 'cost')
    def _compute_total(self):
        for record in self:
            record.total = record.quantity * record.cost

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id