# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_done(self):
        res = super().action_done()
        # Update purchase_price in so_lines
        pickings = self.filtered(
            lambda x: x.picking_type_code == 'outgoing')
        so_lines = pickings.mapped(
            'move_lines.sale_line_id')
        for line in so_lines:
            line.purchase_price = line.product_id.standard_price
        return res
