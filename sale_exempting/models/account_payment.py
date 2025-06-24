from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def default_has_group(self):
        if self.env.user.has_group('sale_exempting.can_view_fictitious_invoices'):
            return True
        else:
            return False

    is_real = fields.Boolean(
        string='Is real',
        default="True",
        required=False)
    payment_mode = fields.Selection(
        string='Payment mode',
        selection=[('check', 'Par chèque'),
                   ('virement', 'Virement bancaire'),
                   ('cash', 'Espèce'),
                   ('bank', 'Versement bancaire'),
                   ],
        required=False)
    virement_number = fields.Char(string='Numéro de virement')
    versement_number = fields.Char(string='Numéro de versement')

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        required=False)
    
    is_invisible = fields.Boolean(
        string='Is_invisible', 
        required=False)

    has_group = fields.Boolean(
        string='Has_group',
        default=default_has_group,
        compute="compute_has_group",
        required=False)

    check_number = fields.Char(string='Numéro de chèque')

    def compute_has_group(self):
        for record in self:
            if self.env.user.has_group('sale_exempting.can_view_fictitious_invoices'):
                record.has_group = True
            else:
                record.has_group = False

    @api.constrains('is_real', 'is_fictitious')
    def _check_sale_type(self):
        for record in self:
            if not record.is_real and not record.is_fictitious and record.partner_type == 'customer':
                raise ValidationError(_('Payment must be real or declared'))



