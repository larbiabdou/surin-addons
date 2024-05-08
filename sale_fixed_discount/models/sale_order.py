from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Monetary(string='Discount Amount', compute="compute_discount_amount")
    total_without_discount = fields.Monetary(string='Total without discount', compute="compute_discount_amount")

    def compute_discount_amount(self):
        for record in self:
            record.discount_amount = sum(line.discount_amount for line in record.order_line)
            record.total_without_discount = sum(line.total_without_discount for line in record.order_line)
            if any(line.price_unit < 0 and line.discount == 0 for line in record.order_line):
                record.discount_amount = abs(sum(line.price_subtotal for line in record.order_line.filtered(lambda line: line.price_unit < 0 and line.discount == 0)))
                record.total_without_discount = record.amount_untaxed + record.discount_amount
