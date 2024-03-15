from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_real = fields.Boolean(
        string='Is real',
        required=False)

    fictitious_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Fictitious invoice',
        required=False)

    count_fictitious_invoices = fields.Integer(
        string='Count_fictitious_invoices',
        compute="compute_count_fictitious_invoices",
        required=False)

    def compute_count_fictitious_invoices(self):
        for record in self:
            record.count_fictitious_invoices = self.env['account.move'].search_count([('fictitious_invoice_id', '=', record.id)])

    def action_get_fictitious_invoices(self):
        self.ensure_one()
        fictitious_invoices = self.env['account.move'].search([('fictitious_invoice_id', '=', self.id)])

        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': {'fictitious_invoice_id': self.id}
        }
        if len(fictitious_invoices) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': fictitious_invoices[0].id,
            })
        elif len(fictitious_invoices) > 1:
            action.update({
                'name': "Factures Fictives",
                'domain': [('id', 'in', fictitious_invoices.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def create_invoice_duplicated(self):
        types = self.invoice_line_ids.mapped('product_id.sale_type')
        if types:
            for type in types:
                new_move_lines = []
                invoice_lines = self.env['account.move.line'].search([('move_id', '=', self.id),
                                                                      ('product_id.sale_type', '=', type)])
                for line in invoice_lines:
                    if line.remaining_qty_not_declared != 0:
                        self.copy({'is_real': False,
                                   'fictitious_invoice_id': self.id,
                                   'invoice_line_ids': new_move_lines})
                        new_line = line.copy({'move_id': False})
                        new_line.update({'quantity': line.remaining_qty_not_declared})
                        new_move_lines.append(new_line)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_real = fields.Boolean(
        string='Is real',
        related="move_id.is_real",
        required=False)

    remaining_qty_not_declared = fields.Float(
        string='Remaining_qty_not_declared',
        compute="compute_remaining_qty",
        required=False)

    def compute_remaining_qty(self):
        for record in self:
            fictitious_invoice_lines = self.env['account.move.line'].search([('move_id.fictitious_invoice_id', '=', record.move_id.id),
                                                                             ('product_id', '=', record.product_id.id)])
            if fictitious_invoice_lines:
                record.remaining_qty_not_declared = record.quantity - sum(line.quantity for line in fictitious_invoice_lines)
            else:
                record.remaining_qty_not_declared = record.quantity

