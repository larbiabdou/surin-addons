from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_type = fields.Selection(
        string='Sale type',
        selection=[('type_1', 'type 1'),
                   ('type_2', 'Type 2'), ],
        required=True, )


