from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # is_real = fields.Boolean(
    #     string='Is real',
    #     required=False)

    is_real = fields.Selection(
        string='Type de vente',
        selection=[('yes', 'Vente sur BL'),
                   ('no', 'Vente déclarée'), ],
        required=True, )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_real', '=', True), ('company_id', 'in', (False, company_id))]")

    delivery_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Delivery_id',
        required=False)

    def check_sale_types(self):
        """Vérifie si la vente contient un seul ou plusieurs types de vente"""
        sale_types = set()
        for line in self.order_line:
            if line.product_id and line.product_id.sale_type:
                sale_types.add(line.product_id.sale_type)

        return {
            'count': len(sale_types),
            'types': list(sale_types),
            'has_multiple_types': len(sale_types) > 1
        }

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