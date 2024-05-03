from odoo import api, fields, models
from odoo.tools.misc import clean_context, formatLang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tax_stamp_amount = fields.Float(
        string='Tax_stamp_amount', 
        required=False)
    is_stamp_tax = fields.Boolean(
        string='Tax stamp',
        required=False)

    # @api.onchange('is_stamp_tax')
    # def onchange_is_stamp_tax(self):
    #     for order in self:
    #         order._compute_amounts()
    #         order._compute_tax_totals()

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'is_stamp_tax')
    def _compute_amounts(self):
        super(SaleOrder, self)._compute_amounts()
        for order in self:
            if order.is_stamp_tax:
                order.tax_stamp_amount = max(order.company_id.stamp_amount_min, min(order.amount_untaxed * order.company_id.stamp_percentage / 100, order.company_id.stamp_amount_max))
                order.amount_total += order.tax_stamp_amount
            else:
                order.tax_stamp_amount = 0


    @api.depends_context('lang')
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id', 'is_stamp_tax')
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for order in self:
            if order.is_stamp_tax:
                tax_totals = order.tax_totals
                tax_stamp_amount = max(order.company_id.stamp_amount_min, min(order.amount_untaxed * order.company_id.stamp_percentage / 100, order.company_id.stamp_amount_max))
                amount_total = order.amount_total
                order.tax_totals['amount_total'] = amount_total
                order.tax_totals['amount_stamp'] = order.tax_stamp_amount
                order.tax_totals['formatted_amount_stamp'] = formatLang(self.env, order.tax_stamp_amount, currency_obj=order.currency_id)
                order.tax_totals['formatted_amount_total'] = formatLang(self.env, amount_total, currency_obj=order.currency_id)
                order.tax_totals['formatted_amount_totals'] = formatLang(self.env, amount_total, currency_obj=order.currency_id)
            else:
                order.tax_totals['formatted_amount_totals'] = formatLang(self.env, order.amount_total, currency_obj=order.currency_id)
