from odoo import api, fields, models
from odoo.tools.misc import clean_context, formatLang


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_stamp_amount = fields.Float(
        string='Tax_stamp_amount',
        required=False)
    is_stamp_tax = fields.Boolean(
        string='Tax stamp',
        required=False)

    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id', 'is_stamp_tax'
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for order in self:
            if order.is_stamp_tax:
                amount_total = order.amount_total
                order.tax_totals['amount_total'] = amount_total
                order.tax_totals['amount_stamp'] = order.tax_stamp_amount
                order.tax_totals['formatted_amount_stamp'] = formatLang(self.env, order.tax_stamp_amount, currency_obj=order.currency_id)
                order.tax_totals['formatted_amount_total'] = formatLang(self.env, amount_total, currency_obj=order.currency_id)
                order.tax_totals['formatted_amount_totals'] = formatLang(self.env, amount_total, currency_obj=order.currency_id)
            else:
                order.tax_totals['formatted_amount_totals'] = formatLang(self.env, order.amount_total, currency_obj=order.currency_id)

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state', 'is_stamp_tax')
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        for move in self:
            if move.is_stamp_tax:
                move.tax_stamp_amount = max(move.company_id.stamp_amount_min, min(move.amount_untaxed * move.company_id.stamp_percentage / 100, move.company_id.stamp_amount_max))
                move.amount_total += move.tax_stamp_amount
                move.amount_total_in_currency_signed += move.tax_stamp_amount
                move.amount_total_signed += move.tax_stamp_amount
                move.amount_residual_signed += move.tax_stamp_amount
                move.amount_residual += move.tax_stamp_amount


            else:
                move.tax_stamp_amount = 0
