from odoo import api, fields, models


class InvoiceType(models.Model):
    _name = 'account.move.type'
    _description = 'Invoice Type'

    name = fields.Char(string="Name")