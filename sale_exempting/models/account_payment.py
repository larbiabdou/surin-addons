from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_real = fields.Boolean(
        string='Is real',
        default="True",
        required=False)

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        required=False)

    @api.constrains('is_real', 'is_fictitious')
    def _check_sale_type(self):
        for record in self:
            if not record.is_real and not record.is_fictitious and record.partner_type == 'customer':
                raise ValidationError(_('Payment must be real or declared'))



