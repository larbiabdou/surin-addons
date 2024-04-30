from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_name_type_1 = fields.Char(
        string='Nom de la société',
        required=False)

    fax = fields.Char(
        string='Fax',
        required=False)

    rc_1 = fields.Char(
        string='RC', 
        required=False)
    nif = fields.Char(
        string='NIF',
        required=False)
    ai = fields.Char(
        string='AI',
        required=False)
    nis = fields.Char(
        string='NIS',
        required=False)

    nif_1 = fields.Char(
        string='NIF',
        required=False)
    ai_1 = fields.Char(
        string='AI',
        required=False)
    nis_1 = fields.Char(
        string='NIS',
        required=False)

    street_1 = fields.Char()
    street2_1 = fields.Char()
    zip_1 = fields.Char()
    city_1 = fields.Char()
    state_id_1 = fields.Many2one('res.country.state',
        string="Fed. State", domain="[('country_id', '=?', country_id_1)]"
    )
    country_id_1 = fields.Many2one('res.country', string="Country")

    company_name_type_2 = fields.Char(
        string='Nom de la société',
        required=False)

    rc_2 = fields.Char(
        string='RC',
        required=False)
    nif_2 = fields.Char(
        string='NIF',
        required=False)
    ai_2 = fields.Char(
        string='AI',
        required=False)
    nis_2 = fields.Char(
        string='NIS',
        required=False)

    street_2 = fields.Char()
    street2_2 = fields.Char()
    zip_2 = fields.Char()
    city_2 = fields.Char()
    state_id_2 = fields.Many2one('res.country.state',
        string="Fed. State", domain="[('country_id', '=?', country_id_2)]"
    )
    country_id_2 = fields.Many2one('res.country', string="Country")


class BaseDocumentLayout(models.TransientModel):

    _inherit = 'base.document.layout'

    fax = fields.Char(
        string='Fax',
        related='company_id.fax',
        required=False)
    

