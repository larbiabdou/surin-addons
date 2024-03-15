from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_real = fields.Boolean(
        string='Is real',
        required=False)

    @api.onchange('partner_id')
    def onchange_customer_id(self):
        for record in self:
            if record.partner_id and record.partner_id.is_real:
                record.is_real = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date_order'])
                ) if 'date_order' in vals else None
                if vals['is_real'] == True:
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'sale.order.exempt', sequence_date=seq_date) or _("New")

        return super().create(vals_list)
