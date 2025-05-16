# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from ast import literal_eval

from odoo import Command, models, fields, api, _


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    is_real = fields.Boolean(
        string='Is real',
        compute="_compute_real_from_moves",
        store=True,
        required=False)

    is_fictitious = fields.Boolean(
        string='Is Fictitious',
        compute="_compute_real_from_moves",
        store=True,
        required=False)

    @api.depends('move_ids')
    def _compute_real_from_moves(self):
        for record in self:
            move_ids = record.move_ids._origin
            record.is_real = move_ids.is_real if len(move_ids) == 1 else (any(
                move.is_real for move in move_ids))
            record.is_fictitious = move_ids.is_fictitious if len(move_ids) == 1 else (any(
                move.is_fictitious for move in move_ids))

