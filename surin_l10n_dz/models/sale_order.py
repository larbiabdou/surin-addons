from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_total_words = fields.Char(
        string="Amount total in words",
        compute="_compute_amount_total_words",
    )

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words(self):
        for sale in self:
            sale.amount_total_words = sale.currency_id.amount_to_text(sale.amount_total).replace(',', '')


