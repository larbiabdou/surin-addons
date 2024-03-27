from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # def default_has_group(self):
    #     if self.env.user.has_group('sale_exempting.can_view_fictitious_invoices'):
    #         return True
    #     else:
    #         return False

    is_real = fields.Boolean(
        string='Is real',
        required=False)    
    
    fictitious_id = fields.Many2one(
        comodel_name='res.partner',
        string='fictitious customer',
        required=False)

    # has_group = fields.Boolean(
    #     string='Has_group',
    #     default=default_has_group,
    #     compute="compute_has_group",
    #     required=False)
    #
    # def compute_has_group(self):
    #     for record in self:
    #         record.has_group = False
    #         if self.env.user.has_group('sale_exempting.can_view_fictitious_invoices'):
    #             record.has_group = True
    #         else:
    #             record.has_group = False
