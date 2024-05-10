# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stamp_percentage = fields.Float(
        string='Stamp percentage',
        related='company_id.stamp_percentage',
        readonly=False,
        required=False)

    stamp_amount_max = fields.Float(
        string='Maximum value',
        related='company_id.stamp_amount_max',
        readonly=False,
        required=False)

    stamp_amount_min = fields.Float(
        string='Minimum value',
        related='company_id.stamp_amount_min',
        readonly=False,
        required=False)