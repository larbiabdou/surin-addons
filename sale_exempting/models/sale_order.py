from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # is_real = fields.Boolean(
    #     string='Is real',
    #     required=False)

    is_real = fields.Selection(
        string='Is real',
        selection=[('yes', 'Yes'),
                   ('no', 'No'), ],
        required=True, )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_real', '=', True), ('company_id', 'in', (False, company_id))]")

    delivery_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Delivery_id',
        required=False)

    @api.onchange('partner_id')
    def onchange_customer_id(self):
        for record in self:
            if record.partner_id and record.partner_id.is_real and (not record.partner_id.fictitious_id or record.partner_id.fictitious_id != record.partner_id):
                record.is_real = 'yes'
                record.journal_id = self.env.ref('sale_exempting.journal_sale_exempting').id
            elif record.partner_id and record.partner_id.is_real and record.partner_id.fictitious_id and record.partner_id.fictitious_id == record.partner_id:
                record.is_real = 'no'
                record.journal_id = False
            else:
                record.is_real = 'no'
                record.journal_id = False

    @api.onchange('is_real')
    def onchange_is_real(self):
        if self.is_real == 'yes':
            self.journal_id = self.env.ref('sale_exempting.journal_sale_exempting').id
        else:
            self.journal_id = False

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['is_real'] = True
        invoice_vals['is_fictitious'] = True if self.is_real == 'no' else False
        invoice_vals['delivery_id'] = self.delivery_id.id
        return invoice_vals

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('name', _("New")) == _("New"):
    #             seq_date = fields.Datetime.context_timestamp(
    #                 self, fields.Datetime.to_datetime(vals['date_order'])
    #             ) if 'date_order' in vals else None
    #             if 'is_real' in vals and vals['is_real'] == 'yes':
    #                 vals['name'] = self.env['ir.sequence'].next_by_code(
    #                     'sale.order.exempt', sequence_date=seq_date) or _("New")
    #
    #     return super().create(vals_list)
