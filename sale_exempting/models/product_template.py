from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_type = fields.Selection(
        string='Sale type',
        selection=[('type_1', 'Produits de négoce'),
                   ('type_2', 'Produits de fabrication')])


