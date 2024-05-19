from odoo import api, fields, models, _
from odoo.tools.misc import clean_context, formatLang
from collections import defaultdict


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tax_stamp_amount = fields.Float(
        string='Tax_stamp_amount',
        compute="compute_tax_stamp",
        store=True,
        required=False)
    is_stamp_tax = fields.Boolean(
        string='Tax stamp',
        required=False)

    total_ttc_without_stamp = fields.Float(
        string='Total_ttc_without_stamp',
        compute="compute_tax_stamp",
        required=False)

    def _get_order_lines_to_report(self):
        down_payment_lines = self.order_line.filtered(lambda line:
            line.is_downpayment
            and not line.display_type
            and not line._get_downpayment_state()
        )
        product_stamp = self.env.ref('l10n_dz_stamp.product_product_service_stamp', raise_if_not_found=False)
        def show_line(line):
            if line.product_id.id == product_stamp.id or line.price_unit < 0:
                return False
            elif not line.is_downpayment:
                return True
            elif line.display_type and down_payment_lines:
                return True  # Only show the down payment section if down payments were posted
            elif line in down_payment_lines:
                return True  # Only show posted down payments
            else:
                return False

        return self.order_line.filtered(show_line)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['is_stamp_tax'] = self.is_stamp_tax
        return invoice_vals

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'is_stamp_tax')
    def compute_tax_stamp(self):
        product_stamp = self.env.ref('l10n_dz_stamp.product_product_service_stamp', raise_if_not_found=False)
        for order in self:
            if order.is_stamp_tax and order.amount_total > 0:
                amount_subtotal = 0
                for line in order.order_line.filtered(lambda l: l.product_id.id != product_stamp.id):
                    if not line.product_uom_qty or not line.price_unit:
                        continue

                    amount_subtotal += line.price_total if line.product_id != product_stamp else 0

                order.tax_stamp_amount = max(order.company_id.stamp_amount_min, min(amount_subtotal * order.company_id.stamp_percentage / 100, order.company_id.stamp_amount_max))
                order.total_ttc_without_stamp = order.amount_total - order.tax_stamp_amount
                if not any(line.product_id.id == product_stamp.id for line in order.order_line):
                    vals = {
                        'order_id': order._origin.id,
                        'product_id': product_stamp.id,
                        'sequence': 999,
                        'tax_id': False,
                        'price_unit': max(order.company_id.stamp_amount_min, min(amount_subtotal * order.company_id.stamp_percentage / 100, order.company_id.stamp_amount_max)),
                    }
                    self.env['sale.order.line'].create(vals)
                else:
                    lines = order.order_line.filtered(lambda l: l.product_id.id == product_stamp.id)
                    lines.update({
                        'price_unit': max(order.company_id.stamp_amount_min, min(amount_subtotal * order.company_id.stamp_percentage / 100, order.company_id.stamp_amount_max)),
                    })

            elif not order.is_stamp_tax:
                order.tax_stamp_amount = 0
                if any(line.product_id.id == product_stamp.id for line in order.order_line):
                    lines = order.order_line.filtered(lambda l: l.product_id.id == product_stamp.id)
                    order.order_line = [(3, line.id) for line in lines]

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'is_stamp_tax')
    def _compute_amounts(self):
        super(SaleOrder, self)._compute_amounts()
        for order in self:
            if order.is_stamp_tax and order.amount_total > 0:
                order.amount_untaxed -= order.tax_stamp_amount
            else:
                order.tax_stamp_amount = 0

    @api.depends_context('lang')
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id', 'is_stamp_tax')
    def _compute_tax_totals(self):
        super()._compute_tax_totals()
        for order in self:
            if order.is_stamp_tax and order.amount_total > 0:
                amount_untaxed = order.amount_untaxed
                order.tax_totals['amount_stamp'] = order.tax_stamp_amount
                order.tax_totals['formatted_amount_stamp'] = formatLang(self.env, order.tax_stamp_amount, currency_obj=order.currency_id)
                if 'subtotals' in order.tax_totals and order.tax_totals['subtotals']:
                    order.tax_totals['subtotals'][0]['formatted_amounts'] = formatLang(self.env, amount_untaxed, currency_obj=order.currency_id)
                    order.tax_totals['subtotals'][0]['formatted_amount'] = formatLang(self.env, amount_untaxed, currency_obj=order.currency_id)
                order.tax_totals['formatted_subtotal_amount'] = formatLang(self.env, amount_untaxed, currency_obj=order.currency_id)
                order.tax_totals['total_ttc_without_stamp'] = formatLang(self.env, order.total_ttc_without_stamp, currency_obj=order.currency_id)
            elif order.amount_total > 0:
                if 'subtotals' in order.tax_totals and order.tax_totals['subtotals']:
                    order.tax_totals['subtotals'][0]['formatted_amounts'] = formatLang(self.env, order.amount_untaxed, currency_obj=order.currency_id)
                order.tax_totals['formatted_subtotal_amount'] = formatLang(self.env, order.amount_untaxed, currency_obj=order.currency_id)


class SaleOrderDiscount(models.TransientModel):
    _inherit = 'sale.order.discount'

    def action_apply_discount(self):
        product_stamp = self.env.ref('l10n_dz_stamp.product_product_service_stamp', raise_if_not_found=False)
        self.ensure_one()
        self = self.with_company(self.company_id)
        if self.discount_type == 'sol_discount':
            self.sale_order_id.order_line.filtered(lambda l: l.product_id.id != product_stamp.id).write({'discount': self.discount_percentage*100})
        else:
            self._create_discount_lines()
        self.sale_order_id.compute_tax_stamp()

    def _create_discount_lines(self):
        """Create SOline(s) according to wizard configuration"""
        self.ensure_one()

        discount_product = self.company_id.sale_discount_product_id
        product_stamp = self.env.ref('l10n_dz_stamp.product_product_service_stamp', raise_if_not_found=False)
        if not discount_product:
            self.company_id.sale_discount_product_id = self.env['product.product'].create(
                self._prepare_discount_product_values()
            )
            discount_product = self.company_id.sale_discount_product_id

        if self.discount_type == 'amount':
            vals_list = [
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=self.discount_amount,
                    taxes=self.env['account.tax'],
                )
            ]
        else: # so_discount
            total_price_per_tax_groups = defaultdict(float)
            for line in self.sale_order_id.order_line:
                if not line.product_uom_qty or not line.price_unit or line.product_id.id == product_stamp.id:
                    continue

                total_price_per_tax_groups[line.tax_id] += line.price_subtotal

            if not total_price_per_tax_groups:
                # No valid lines on which the discount can be applied
                return
            elif len(total_price_per_tax_groups) == 1:
                # No taxes, or all lines have the exact same taxes
                taxes = next(iter(total_price_per_tax_groups.keys()))
                subtotal = total_price_per_tax_groups[taxes]
                vals_list = [{
                    **self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount: %(percent)s%%",
                            percent=self.discount_percentage*100
                        ),
                    ),
                }]
            else:
                vals_list = [
                    self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount: %(percent)s%%"
                            "- On products with the following taxes %(taxes)s",
                            percent=self.discount_percentage*100,
                            taxes=", ".join(taxes.mapped('name'))
                        ),
                    ) for taxes, subtotal in total_price_per_tax_groups.items()
                ]
        return self.env['sale.order.line'].create(vals_list)