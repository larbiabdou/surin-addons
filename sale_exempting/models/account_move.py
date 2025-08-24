from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def default_has_group(self):
        if self.env.user.has_group('sale_exempting.can_view_fictitious_invoices'):
            return True
        else:
            return False

    invoice_real_name = fields.Char(
        string='Vente valorisée',
        default="Vente valorisée",
        required=False)

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
        string='Quantité restante non déclaré',
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
        store=True,
        selection=[('type_1', 'Produits de négoce'),
                   ('type_2', 'Produits de fabrication') ])

    has_group = fields.Boolean(
        string='Has_group',
        default=default_has_group,
        compute="compute_has_group",
        required=False)

    declaration_state = fields.Selection(
        string='Status de déclaration',
        selection=[('not_declared', 'Non déclaré'),
                   ('partially', 'Parciellement déclaré'),
                   ('full', 'Déclaré')],
        compute="compute_remaining_qty",
        required=False, )

    @api.depends('payment_state')
    def _compute_payment_reference(self):
        """Compute payment reference from linked payments"""
        for move in self:
            if move.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
                # Récupérer SEULEMENT les paiements de CETTE facture
                payments = self.env['account.payment'].search([
                ]).filtered(lambda l: move.id in l.reconciled_invoice_ids.ids)

                if payments:
                    payment_names = payments.mapped('name')
                    move.payment_reference = ', '.join(payment_names)
                else:
                    move.payment_reference = False
            else:
                move.payment_reference = False

    def _inverse_payment_reference(self):
        """Allow manual modification"""
        pass

    def compute_has_group(self):
        for record in self:
            if self.env.user.has_group('sale_exempting.can_view_fictitious_invoices'):
                record.has_group = True
            else:
                record.has_group = False

    @api.constrains('is_real', 'is_fictitious')
    def _check_invoice_type(self):
        for record in self:
            if not record.is_real and not record.is_fictitious and record.move_type == 'out_invoice':
                raise ValidationError(_('Sale Invoice must be real or declared'))

    @api.depends('is_real', 'is_fictitious')
    def compute_invoice_types(self):
        real = self.env.ref('surin_l10n_dz.invoice_type_real', raise_if_not_found=False)
        declared = self.env.ref('surin_l10n_dz.invoice_type_declared', raise_if_not_found=False)
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

    @api.depends('invoice_line_ids')
    def compute_sale_type(self):
        for record in self:
            record.sale_type = ''
            line = record.invoice_line_ids.filtered(lambda line: line.product_id.sale_type != '')
            if line:
                record.sale_type = line[0].product_id.sale_type

    def _search_default_journal(self):
        journal = super(AccountMove, self)._search_default_journal()
        if self.is_fictitious and self.move_type == 'out_invoice':
            if self.sale_type == 'type_1':
                journal = self.env.ref('account.1_sale', raise_if_not_found=False).id
            else:
                journal = self.env.ref('sale_exempting.journal_sale_declared', raise_if_not_found=False).id
        return journal

    @api.constrains('invoice_line_ids')
    def _check_sale_type(self):
        for record in self:
            if record.is_fictitious and record.move_type == 'out_invoice':
                sale_type = ''
                for line in record.invoice_line_ids:
                    if line.product_id.sale_type == '' and line.product_id.detailed_type == 'product':
                        raise ValidationError(_('Sale type must not be empty in any product'))
                    elif sale_type != '' and sale_type != line.product_id.sale_type and line.product_id.detailed_type == 'product':
                        raise ValidationError(_('All product must have the same sale type'))
                    else:
                        sale_type = line.product_id.sale_type

    def compute_customers_domain(self):
        for record in self:
            record.customers_domain = self.env['res.partner'].search([])
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
            if record.is_fictitious:
                record.declaration_state = 'full'
            else:
                if record.remaining_qty_not_declared == sum(line.quantity for line in record.invoice_line_ids.filtered(lambda line: line.product_id.detailed_type == 'product')):
                    record.declaration_state = 'not_declared'
                elif record.remaining_qty_not_declared != 0:
                    record.declaration_state = 'partially'
                elif record.remaining_qty_not_declared == 0:
                    record.declaration_state = 'full'


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
        discount_line = False
        if any(line.price_unit < 0 and line.discount == 0 for line in self.invoice_line_ids):
            discount_line = self.env['account.move.line'].search([('move_id', '=', self.id),
                                                                  ('price_unit', '<', 0)])
        types_in_lines = []
        for line in self.invoice_line_ids:
            if line.product_id.sale_type not in types_in_lines and line.product_id.detailed_type == 'product':
                types_in_lines.append(line.product_id.sale_type)
        types_number = len(types_in_lines)
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
                        'discount_fixed': line.discount_fixed,
                        'price_unit': line.price_unit,
                        'real_line_id': line.id,
                        'tax_ids': [(6, 0, line.tax_ids.ids)],
                    })
            if discount_line and new_move_lines != []:
                new_move_lines.append({
                    'name': discount_line.name,
                    'product_id': discount_line.product_id.id,
                    'product_uom_id': discount_line.product_uom_id.id,
                    'quantity': 1,
                    'price_unit': discount_line.price_unit / types_number,
                    'real_line_id': discount_line.id,
                    'tax_ids': False,
                })
            if new_move_lines:
                if type == 'type_1':
                    journal_id = self.env.ref('account.1_sale', raise_if_not_found=False)
                else:
                    journal_id = self.env.ref('sale_exempting.journal_sale_declared', raise_if_not_found=False)
                move_id = self.env['account.move'].create(
                    {
                        'move_type': self.move_type,
                        'partner_id': False,
                        'invoice_date': fields.Date.today(),
                        'journal_id': journal_id.id,
                        'real_invoice_id': self.id,
                        'is_fictitious': True,
                        'is_real': False,
                        'is_stamp_tax': self.is_stamp_tax,
                        #'type': type,
                        'invoice_line_ids': [(0, 0, line) for line in new_move_lines],
                    })

    should_generate_new = fields.Boolean(
        string=' should_generate_new',
        default=True,
        required=False)

    def action_post(self):
        super(AccountMove, self).action_post()
        if self.move_type == 'out_invoice':
            if self.is_fictitious:
                delivery = self.env['stock.picking.fictitious'].search([('invoice_id', '=', self.id)])
                if not delivery:
                    self.create_fictitious_delivery()

                if self.sale_type == 'type_1':
                    # Récupérer le préfixe de la séquence type1
                    sequence_type1 = self.env['ir.sequence'].search(
                        [('code', '=', 'real.invoice.fictitious.type1')], limit=1)
                    prefix_type1 = sequence_type1.prefix if sequence_type1 else 'TYPE1/'

                    if self.should_generate_new:
                        self.name = self.env['ir.sequence'].next_by_code('real.invoice.fictitious.type1') or _(
                            'New')
                        self.should_generate_new = False
                else:
                    # Récupérer le préfixe de la séquence type2
                    sequence_type2 = self.env['ir.sequence'].search(
                        [('code', '=', 'real.invoice.fictitious.type2')], limit=1)
                    prefix_type2 = sequence_type2.prefix if sequence_type2 else 'TYPE2/'

                    if self.should_generate_new:
                        self.name = self.env['ir.sequence'].next_by_code('real.invoice.fictitious.type2') or _(
                            'New')
                        self.should_generate_new = False

            elif self.is_real and self.delivery_id and not self.is_fictitious:
                list = self.delivery_id.name.rsplit('/')
                sequence = self.env['ir.sequence'].search([('code', '=', 'real.invoice')], limit=1)
                prefix = sequence[0]._get_prefix_suffix()[0]
                self.name = prefix + list[len(list)-1]

    def create_fictitious_delivery(self):
        delivery_id = False
        domain = []
        if self.delivery_id:
            delivery_id = self.delivery_id
            domain = [('id', 'in', delivery_id.move_ids_without_package.ids)]
        elif self.real_invoice_id and self.real_invoice_id.delivery_id:
            delivery_id = self.real_invoice_id.delivery_id
            domain = [('sale_line_id', 'in', self.invoice_line_ids.real_line_id.sale_line_ids.ids), ('picking_id', '=', delivery_id.id)]
        if delivery_id:
            stock_moves = self.env['stock.move'].search(domain)
            if stock_moves:
                fictitious_transfer = self.env['stock.picking.fictitious'].create({
                    'operation_type_id': delivery_id.picking_type_id.id,
                    'scheduled_date': delivery_id.scheduled_date,
                    'origin': self.name,
                    'invoice_id': self.id,
                    'delivery_id': delivery_id.id,
                })
                for line in stock_moves:
                    fictitious_transfer.operation_ids = [(0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'quantity': line.quantity,
                        'product_uom': line.product_uom.id,
                        'stock_move_id': line.id,
                        'detailed_operation_ids': [(0, 0, {
                            'product_id': mv_line.product_id.id,
                            'quantity': mv_line.quantity,
                            'product_uom': mv_line.product_uom_id.id,
                            'lot_id': mv_line.lot_id.id}) for mv_line in line.move_line_ids],
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
        string='Quantité restante non déclaré',
        compute="compute_remaining_qty",
        required=False)
    real_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Real_line_id',
        required=False)

    @api.depends('is_real', 'is_fictitious')
    def compute_invoice_types(self):
        real = self.env.ref('surin_l10n_dz.invoice_type_real', raise_if_not_found=False)
        declared = self.env.ref('surin_l10n_dz.invoice_type_declared', raise_if_not_found=False)
        for record in self:
            record.invoice_types = False
            if record.is_real:
                record.invoice_types = [(4, real.id)]
            if record.is_fictitious:
                record.invoice_types = [(4, declared.id)]

    def compute_remaining_qty(self):
        for record in self:
            if record.product_id.detailed_type != 'product':
                record.remaining_qty_not_declared = 0
            else:
                fictitious_invoice_lines = self.env['account.move.line'].search([('move_id.real_invoice_id', '=', record.move_id.id),
                                                                                 ('product_id', '=', record.product_id.id),
                                                                                 ('product_id.detailed_type', '=', 'product'),
                                                                                 ('move_id.state', '=', 'posted')])
                if fictitious_invoice_lines:
                    record.remaining_qty_not_declared = record.quantity - sum(line.quantity for line in fictitious_invoice_lines)
                else:
                    record.remaining_qty_not_declared = record.quantity


