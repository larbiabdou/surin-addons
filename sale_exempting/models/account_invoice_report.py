from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    is_real = fields.Boolean(
        string='Is real',
        required=False)

    is_fictitious = fields.Boolean(
        string='Is fictitious',
        required=False)

    def _select(self):
        return super()._select() + ", move.is_real as is_real, move.is_fictitious as is_fictitious"