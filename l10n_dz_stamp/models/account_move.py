from odoo import api, fields, models
from odoo.tools.misc import clean_context, formatLang
from odoo import api, fields, models, _, Command


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_stamp_amount = fields.Float(
        string='Tax_stamp_amount',
        compute="compute_tax_stamp",
        store=True,
        required=False)

    total_ttc_without_stamp = fields.Float(
        string='Total_ttc_without_stamp',
        compute="compute_tax_stamp",
        required=False)

    is_stamp_tax = fields.Boolean(
        string='Tax stamp',
        required=False)

    discount_amount = fields.Monetary(string='Discount Amount', compute="compute_discount_amount")
    total_without_discount = fields.Monetary(string='Total without discount', compute="compute_discount_amount")

    @api.onchange('payment_mode')
    def _onchange_payment_mode(self):
        for move in self:
            if move.payment_mode == 'cash':
                move.is_stamp_tax = True
            else:
                move.is_stamp_tax = False

    def compute_discount_amount(self):
        for record in self:
            record.discount_amount = sum(line.discount_amount for line in record.invoice_line_ids)
            record.total_without_discount = sum(line.total_without_discount for line in record.invoice_line_ids)
            if any(line.price_unit < 0 and line.discount == 0 for line in record.invoice_line_ids):
                record.discount_amount = abs(sum(line.price_subtotal for line in record.invoice_line_ids.filtered(lambda line: line.price_unit < 0 and line.discount == 0)))
                record.total_without_discount = record.amount_untaxed + record.discount_amount
                if record.is_stamp_tax:
                    record.total_without_discount -= record.tax_stamp_amount

    @api.depends('is_stamp_tax', 'invoice_line_ids')
    def compute_tax_stamp(self):
        product_stamp = self.env.ref('surin_l10n_dz.product_product_service_stamp', raise_if_not_found=False)
        for move in self:
            if move.is_stamp_tax and move.amount_total > 0:
                amount_subtotal = 0
                for line in move.invoice_line_ids.filtered(lambda l: l.product_id.id != product_stamp.id):
                    if not line.quantity or not line.price_unit:
                        continue

                    amount_subtotal += line.price_total if line.product_id != product_stamp else 0
                amount = amount_subtotal
                if amount <= 300:
                    tax_stamp_amount = 0
                elif amount <= 30000:
                    tax_stamp_amount = amount * 0.01  # 1%
                elif amount <= 100000:
                    tax_stamp_amount = amount * 0.015  # 1.5%
                else:
                    tax_stamp_amount = amount * 0.02
                move.tax_stamp_amount = tax_stamp_amount
                move.total_ttc_without_stamp = move.amount_total - move.tax_stamp_amount
                if not any(line.product_id.id == product_stamp.id for line in move.invoice_line_ids):
                    vals = {
                        'move_id': move._origin.id,
                        'product_id': product_stamp.id,
                        'sequence': 999,
                        'tax_ids': False,
                        'price_unit': tax_stamp_amount,
                    }
                    self.env['account.move.line'].create(vals)
                else:
                    lines = move.invoice_line_ids.filtered(lambda l: l.product_id.id == product_stamp.id)
                    lines.update({
                        'price_unit': tax_stamp_amount,
                    })

    def delete_stamp(self):
        for move in self:
            product_stamp = self.env.ref('surin_l10n_dz.product_product_service_stamp', raise_if_not_found=False)
            move.tax_stamp_amount = 0
            if any(line.product_id.id == product_stamp.id for line in move.invoice_line_ids):
                lines = move.invoice_line_ids.filtered(lambda l: l.product_id.id == product_stamp.id)
                move._origin.write({'invoice_line_ids': [Command.delete(line._origin.id) for line in lines]})

    def write(self, values):
        # Add code here
        res = super(AccountMove, self).write(values)
        if 'is_stamp_tax' in values and values['is_stamp_tax'] == False:
            self.delete_stamp()
        return res

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
        for move in self:
            if move.is_stamp_tax and move.amount_total > 0:
                amount_untaxed = move.amount_untaxed
                move.tax_totals['amount_stamp'] = move.tax_stamp_amount
                move.tax_totals['formatted_amount_stamp'] = formatLang(self.env, move.tax_stamp_amount, currency_obj=move.currency_id)
                if 'subtotals' in move.tax_totals and move.tax_totals['subtotals']:
                    move.tax_totals['subtotals'][0]['formatted_amounts'] = formatLang(self.env, amount_untaxed - move.tax_stamp_amount, currency_obj=move.currency_id)
                    move.tax_totals['subtotals'][0]['formatted_amount'] = formatLang(self.env, amount_untaxed - move.tax_stamp_amount, currency_obj=move.currency_id)
                move.tax_totals['formatted_subtotal_amount'] = formatLang(self.env, amount_untaxed - move.tax_stamp_amount, currency_obj=move.currency_id)
                move.tax_totals['total_ttc_without_stamp'] = formatLang(self.env, move.total_ttc_without_stamp, currency_obj=move.currency_id)

            elif move.amount_total > 0:
                if 'subtotals' in move.tax_totals and move.tax_totals['subtotals'][0]:
                    move.tax_totals['subtotals'][0]['formatted_amounts'] = formatLang(self.env, move.amount_untaxed, currency_obj=move.currency_id)
                    move.tax_totals['formatted_subtotal_amount'] = formatLang(self.env, move.amount_untaxed, currency_obj=move.currency_id)

    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.balance',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     'state', 'is_stamp_tax')
    # def _compute_amount(self):
    #     super(AccountMove, self)._compute_amount()
    #     for move in self:
    #         total_untaxed, total_untaxed_currency = 0.0, 0.0
    #         total_tax, total_tax_currency = 0.0, 0.0
    #         total_residual, total_residual_currency = 0.0, 0.0
    #         total, total_currency = 0.0, 0.0
    #         product_stamp = self.env.ref('surin_l10n_dz.product_product_service_stamp', raise_if_not_found=False)
    #         for line in move.line_ids:
    #             if move.is_invoice(True):
    #                 # === Invoices ===
    #                 if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
    #                     # Tax amount.
    #                     total_tax += line.balance
    #                     total_tax_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.display_type in ('product', 'rounding'):
    #                     # Untaxed amount.
    #                     total_untaxed += line.balance if line.product_id.id != product_stamp.id else 0
    #                     total_untaxed_currency += line.amount_currency if line.product_id.id != product_stamp.id else 0
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.display_type == 'payment_term':
    #                     # Residual amount.
    #                     total_residual += line.amount_residual
    #                     total_residual_currency += line.amount_residual_currency
    #             else:
    #                 # === Miscellaneous journal entry ===
    #                 if line.debit:
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #
    #         sign = move.direction_sign
    #         move.amount_untaxed = sign * total_untaxed_currency
    #         move.amount_tax = sign * total_tax_currency
    #         move.amount_total = sign * total_currency
    #         move.amount_residual = -sign * total_residual_currency
    #         move.amount_untaxed_signed = -total_untaxed
    #         move.amount_tax_signed = -total_tax
    #         move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
    #         move.amount_residual_signed = total_residual
    #         move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)

