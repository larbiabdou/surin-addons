from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_real = fields.Boolean(
        string='Is real',
        required=False)

