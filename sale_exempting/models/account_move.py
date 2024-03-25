from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_types = fields.Many2many(
        comodel_name='account.move.type',
        compute="compute_invoice_types",
        relation="account_invoice_invoice_type_rel",
        store=True,
        string='Types de facture')

    is_real = fields.Boolean(
        string='Is real',
        default="True",
        required=False)

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        required=False)

    real_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Fictitious invoice',
        required=False)

    count_fictitious_invoices = fields.Integer(
        string='Count_fictitious_invoices',
        compute="compute_count_fictitious_invoices",
        required=False)

    remaining_qty_not_declared = fields.Float(
        string='Remaining_qty_not_declared',
        compute="compute_remaining_qty",
        required=False)

    delivery_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Delivery_id',
        required=False)

    customers_domain = fields.Many2many(
        comodel_name='res.partner',
        compute="compute_customers_domain")

    sale_type = fields.Selection(
        string='Sale type',
        compute="compute_sale_type",
        selection=[('type_1', 'type 1'),
                   ('type_2', 'Type 2'), ])

    @api.constrains('is_real', 'is_fictitious')
    def _check_sale_type(self):
        for record in self:
            if not record.is_real and not record.is_fictitious and record.move_type == 'out_invoice':
                raise ValidationError(_('Sale Invoice must be real or declared'))

    @api.depends('is_real', 'is_fictitious')
    def compute_invoice_types(self):
        real = self.env.ref('sale_exempting.invoice_type_real', raise_if_not_found=False)
        declared = self.env.ref('sale_exempting.invoice_type_declared', raise_if_not_found=False)
        for record in self:
            record.invoice_types = False
            if record.is_real:
                record.invoice_types = [(4, real.id)]
            if record.is_fictitious:
                record.invoice_types = [(4, declared.id)]

    def unlink(self):
        for record in self:
            delivery = self.env['stock.picking.fictitious'].search([('invoice_id', '=', record.id)])
            if delivery:
                delivery.unlink()
        super(AccountMove, self).unlink()

    def compute_sale_type(self):
        for record in self:
            record.sale_type = ''
            line = record.invoice_line_ids.filtered(lambda line: line.product_id.sale_type != '')
            if line:
                record.sale_type = line[0].product_id.sale_type

    @api.constrains('invoice_line_ids')
    def _check_sale_type(self):
        for record in self:
            if record.is_fictitious and record.move_type == 'out_invoice':
                sale_type = ''
                for line in record.invoice_line_ids:
                    if line.product_id.sale_type == '':
                        raise ValidationError(_('Sale type must not be empty in any product'))
                    elif sale_type != '' and sale_type != line.product_id.sale_type:
                        raise ValidationError(_('All product must have the same sale type'))
                    else:
                        sale_type = line.product_id.sale_type

    @api.onchange('is_real')
    def compute_customers_domain(self):
        for record in self:
            record.customers_domain = False
            if record.move_type == 'out_invoice':
                if record.is_real:
                    record.customers_domain = self.env['res.partner'].search([('is_real', '=', True)])
                else:
                    record.customers_domain = self.env['res.partner'].search([('is_real', '=', False)])

    @api.onchange('partner_id')
    def onchange_customer_id(self):
        for record in self:
            if record.move_type == 'out_invoice':
                if record.partner_id and record.partner_id.is_real and (not record.partner_id.fictitious_id or record.partner_id.fictitious_id != record.partner_id):
                    record.is_real = True
                    record.is_fictitious = False
                elif record.partner_id and record.partner_id.is_real and record.partner_id.fictitious_id and record.partner_id.fictitious_id == record.partner_id:
                    record.is_real = True
                    record.is_fictitious = True

    def compute_remaining_qty(self):
        for record in self:
            record.remaining_qty_not_declared = sum(line.remaining_qty_not_declared for line in record.invoice_line_ids) or 0

    def compute_count_fictitious_invoices(self):
        for record in self:
            record.count_fictitious_invoices = self.env['account.move'].search_count([('real_invoice_id', '=', record.id)])

    def action_get_fictitious_invoices(self):
        self.ensure_one()
        fictitious_invoices = self.env['account.move'].search([('real_invoice_id', '=', self.id)])

        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'real_invoice_id': self.id}
        }
        if len(fictitious_invoices) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': fictitious_invoices[0].id,
            })
        elif len(fictitious_invoices) > 1:
            action.update({
                'name': "Factures Fictives",
                'domain': [('id', 'in', fictitious_invoices.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def create_invoice_duplicated(self):
        types = ['type_1', 'type_2']
        for type in types:
            new_move_lines = []
            invoice_lines = self.env['account.move.line'].search([('move_id', '=', self.id),
                                                                  ('product_id.sale_type', '=', type)])
            for line in invoice_lines:
                if line.remaining_qty_not_declared != 0:
                    #new_line.update({'quantity': line.remaining_qty_not_declared})
                    new_move_lines.append({
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom_id.id,
                        'quantity': line.remaining_qty_not_declared,
                        'discount': line.discount,
                        'price_unit': line.price_unit,
                        'real_line_id': line.id,
                        'tax_ids': [(6, 0, line.tax_ids.ids)],
                    })
            if new_move_lines:
                move_id = self.env['account.move'].create(
                    {
                        'move_type': self.move_type,
                        #'partner_id': self.partner_id.id,
                        'invoice_date': self.invoice_date,
                        'journal_id': self.env.ref('account.1_sale', raise_if_not_found=False).id,
                        'real_invoice_id': self.id,
                        'is_fictitious': True,
                        'is_real': False,
                        #'type': type,
                        'invoice_line_ids': [(0, 0, line) for line in new_move_lines],
                    })

    def action_post(self):
        super(AccountMove, self).action_post()
        if self.move_type == 'out_invoice':
            if self.is_fictitious and self.sale_type != '':
                if self.sale_type == 'type_1':
                    sequence = self.env['ir.sequence'].search([('code', '=', 'declared.invoice.type_1')], limit=1)
                    prefix = sequence[0]._get_prefix_suffix()[0]
                else:
                    sequence = self.env['ir.sequence'].search([('code', '=', 'declared.invoice.type_2')], limit=1)
                    prefix = sequence[0]._get_prefix_suffix()[0]
                if not self.name.startswith(prefix):
                    if self.sale_type == 'type_1':
                        self.name = self.env['ir.sequence'].next_by_code('declared.invoice.type_1') or _("New")
                    else:
                        self.name = self.env['ir.sequence'].next_by_code('declared.invoice.type_2') or _("New")
                delivery = self.env['stock.picking.fictitious'].search([('invoice_id', '=', self.id)])
                if not delivery:
                    self.create_fictitious_delivery()
            elif self.is_real and self.delivery_id:
                list = self.delivery_id.name.rsplit('/')
                sequence = self.env['ir.sequence'].search([('code', '=', 'real.invoice')], limit=1)
                prefix = sequence[0]._get_prefix_suffix()[0]
                self.name = prefix + list[len(list)-1]


    def create_fictitious_delivery(self):
        delivery_id = False
        if self.delivery_id:
            delivery_id = self.delivery_id
        elif self.is_fictitious and not self.is_real and self.real_invoice_id:
            sale_line_ids = self.real_invoice_id.invoice_line_ids.sale_line_ids
            sale_id = sale_line_ids.mapped('order_id')
            if sale_id:
                picking_id = self.env['stock.picking'].search([('sale_id', '=', sale_id.id)])
                if picking_id:
                    delivery_id = picking_id[0]
        if delivery_id:
            fictitious_transfer = self.env['stock.picking.fictitious'].create({
                'partner_id': delivery_id.partner_id.id,
                'operation_type_id': delivery_id.picking_type_id.id,
                'scheduled_date': delivery_id.scheduled_date,
                'origin': self.name,
                'invoice_id': self.id,
            })
            for line in self.invoice_line_ids:
                fictitious_transfer.operation_ids = [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'quantity': line.quantity,
                })]


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_types = fields.Many2many(
        comodel_name='account.move.type',
        compute="compute_invoice_types",
        store=True,
        string='Invoice types')

    is_real = fields.Boolean(
        string='Is real',
        related="move_id.is_real",
        store=True,
        required=False)

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        store=True,
        related="move_id.is_fictitious",
        required=False)

    remaining_qty_not_declared = fields.Float(
        string='Remaining_qty_not_declared',
        compute="compute_remaining_qty",
        required=False)
    real_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Real_line_id',
        required=False)

    @api.depends('is_real', 'is_fictitious')
    def compute_invoice_types(self):
        real = self.env.ref('sale_exempting.invoice_type_real', raise_if_not_found=False)
        declared = self.env.ref('sale_exempting.invoice_type_declared', raise_if_not_found=False)
        for record in self:
            record.invoice_types = False
            if record.is_real:
                record.invoice_types = [(4, real.id)]
            if record.is_fictitious:
                record.invoice_types = [(4, declared.id)]

    def compute_remaining_qty(self):
        for record in self:
            fictitious_invoice_lines = self.env['account.move.line'].search([('move_id.real_invoice_id', '=', record.move_id.id),
                                                                             ('product_id', '=', record.product_id.id)])
            if fictitious_invoice_lines:
                record.remaining_qty_not_declared = record.quantity - sum(line.quantity for line in fictitious_invoice_lines)
            else:
                record.remaining_qty_not_declared = record.quantity


class InvoiceType(models.Model):
    _name = 'account.move.type'
    _description = 'Invoice Type'

    name = fields.Char(string="Name")


