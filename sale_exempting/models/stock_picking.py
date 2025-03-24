from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(readonly=False)

    def button_validate(self):
        super(StockPicking, self).button_validate()

        if self.sale_id:
            self.sale_id.delivery_id = self.id
            payment = self.env['sale.advance.payment.inv'].with_context({
                'active_model': 'sale.order',
                'active_ids': [self.sale_id.id],
                'active_id': self.sale_id.id,
                #'default_journal_id': self.company_data['default_journal_sale'].id,
            }).create({
                'advance_payment_method': 'delivered'
            })
            payment.create_invoices()

