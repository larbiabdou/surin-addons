# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class RepairSparePartReport(models.Model):
    _name = 'repair.spare.part.report'
    _description = 'Spare Part Analysis'
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    id = fields.Integer('ID', readonly=True)
    repair_id = fields.Many2one('repair.order', string='Repair Order', readonly=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number', readonly=True)
    qty_done = fields.Float('Quantity', readonly=True)
    unit_cost = fields.Float('Unit Cost', readonly=True)
    total_cost = fields.Float('Total Cost', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('under_repair', 'Under Repair'),
        ('done', 'Repaired'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)

    def _select(self):
        select_str = """
                min(sml.id) as id,
                r.id as repair_id,
                r.equipment_id as equipment_id,
                sml.product_id as product_id,
                sml.product_uom_id as product_uom_id,
                sml.lot_id as lot_id,
                sml.quantity as qty_done,
                r.company_id as company_id,
                r.create_date as date,
                r.state as state,
                CASE 
                    WHEN SUM(svl.quantity) != 0 THEN SUM(svl.value) / SUM(svl.quantity)
                    ELSE 0 
                END as unit_cost,
                ABS(SUM(COALESCE(svl.value, 0))) as total_cost,
                r.partner_id as partner_id,
                r.user_id as user_id,
                pt.id as product_tmpl_id,
                pt.categ_id as categ_id,
                count(sml.id) as nbr
        """
        return select_str

    def _from(self):
        from_str = """
            stock_move_line sml
            LEFT JOIN stock_move sm ON sm.id = sml.move_id
            LEFT JOIN repair_order r ON sm.repair_id = r.id
            LEFT JOIN product_product pp ON pp.id = sml.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN stock_valuation_layer svl ON svl.stock_move_id = sm.id
        """
        return from_str

    def _where(self):
        where_str = """
            r.id IS NOT NULL
            AND sm.repair_id IS NOT NULL
            AND r.state = 'done'
            AND sm.repair_line_type = 'add'
        """
        return where_str

    def _group_by(self):
        group_by_str = """
            r.id,
            r.equipment_id,
            sml.product_id,
            sml.product_uom_id,
            sml.quantity,
            sml.lot_id,
            r.company_id,
            r.create_date,
            r.state,
            r.partner_id,
            r.user_id,
            pt.id,
            pt.categ_id
        """
        return group_by_str

    def _with_sale(self):
        return ""

    def _query(self):
        with_ = self._with_sale()
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select()}
            FROM {self._from()}
            WHERE {self._where()}
            GROUP BY {self._group_by()}
            {")" if with_ else ""}
        """

    @property
    def _table_query(self):
        return self._query()