from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_total_words = fields.Char(
        string="Amount total in words",
        compute="_compute_amount_total_words",
    )
    payment_mode = fields.Selection(
        string='Payment mode',
        selection=[('check', 'Par chèque'),
                   ('virement', 'Virement bancaire'),
                   ('cash', 'Espèce'),
                   ('bank', 'Versement bancaire'),
                   ],
        required=False, )

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['payment_mode'] = self.payment_mode
        return invoice_vals


    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words(self):
        for sale in self:
            sale.amount_total_words = sale.currency_id.amount_to_text(sale.amount_total).replace(',', '')


