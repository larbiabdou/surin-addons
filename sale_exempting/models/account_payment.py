from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_real = fields.Boolean(
        string='Is real',
        default="True",
        required=False)

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        required=False)



