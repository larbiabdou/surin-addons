from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class StcokPickingFictitious(models.Model):
    _name = 'stock.picking.fictitious'
    _description = 'Fictitious Transfer'

    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice_id',
        required=False)
    name = fields.Char(string='Name', store=True, compute="compute_name")
    state = fields.Selection()
    delivery_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Delivery_id',
        required=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related="invoice_id.partner_id",
        string='Delivery address',
        required=False)
    operation_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Operation',
        required=False)
    scheduled_date = fields.Date(
        string='Scheduled date',
        required=False)
    origin = fields.Char(
        string='Origin', 
        required=False)

    operation_ids = fields.One2many(
        comodel_name='stock.move.fictitious',
        inverse_name='picking_id',
        string='Operations',
        required=False)

    state = fields.Selection(
        string='State',
        related='invoice_id.state',
        selection=[('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),],
        required=False, )
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        related='delivery_id.company_id',
        required=False)

    stock_moves = fields.Many2many(
        comodel_name='stock.move',
        compute="compute_stock_moves",
        string='Stock_moves')
    
    move_type = fields.Selection(related='delivery_id.move_type')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        related='delivery_id.user_id',)
    note = fields.Text(
        string="Note",
        required=False)
    sale_type = fields.Selection(
        string='Sale type',
        related="invoice_id.sale_type")

    def compute_stock_moves(self):
        for record in self:
            record.stock_moves = self.operation_ids.mapped('stock_move_id')

    @api.depends('invoice_id.name')
    def compute_name(self):
        for record in self:
            if record.invoice_id:
                list = self.invoice_id.name.rsplit('/')
                if record.invoice_id.sale_type == 'type_1':
                    sequence = self.env['ir.sequence'].search([('code', '=', 'declared.transfer.type_1')], limit=1)
                else:
                    sequence = self.env['ir.sequence'].search([('code', '=', 'declared.transfer.type_2')], limit=1)
                prefix = sequence[0]._get_prefix_suffix()[0]
                self.name = prefix + list[len(list) - 1]

    def unlink(self):
        for record in self:
            if record.state == 'posted':
                raise ValidationError(_('You can not delete a posted transfer'))
        return super(StcokPickingFictitious, self).unlink()

    def action_detailed_operations(self):
        self.ensure_one()
        detailed_operation = self.operation_ids.detailed_operation_ids

        action = {
            'res_model': 'stock.move.line.fictitious',
            'name': "Detailed Operations",
            'domain': [('id', 'in', detailed_operation.ids)],
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'context': {'create': False},
        }
        return action


class stockMoveFictitious(models.Model):
    _name = 'stock.move.fictitious'
    _description = 'Stock Move Fictitious'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=False)

    product_uom_qty = fields.Float(
        string='Demand', 
        required=False)

    picking_id = fields.Many2one(
        comodel_name='stock.picking.fictitious',
        string='Picking_id',
        required=False)

    quantity = fields.Float(
        string='Quantity', 
        required=False)

    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='Uom',
        required=False)

    detailed_operation_ids = fields.One2many(
        comodel_name='stock.move.line.fictitious',
        inverse_name='move_id',
        string='Operations',
        required=False)

    stock_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock_move_id',
        required=False)


class stockMoveFictitous(models.Model):
    _name = 'stock.move.line.fictitious'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=False)
    
    move_id = fields.Many2one(
        comodel_name='stock.move.fictitious',
        string='Move_id',
        required=False)

    lot_id = fields.Many2one(
        comodel_name='stock.lot',
        string='Lot/serial number',
        required=False)
    
    quantity = fields.Float(
        string='Quantity', 
        required=False)

    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='Uom',
        required=False)

