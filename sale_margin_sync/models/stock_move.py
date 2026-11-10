# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        # Update purchase price from sale line linked to the move
        if "value" in vals and not self.env.context.get("skip_sale_margin_sync", False):
            self.sale_margin_sync()
        return res

    def sale_margin_sync(self):
        """Only synchronize moves that deliver goods to customers (deliveries
        and dropshipments)"""
        moves = self.filtered(
            lambda m: (m._is_out() or m._is_dropshipped()) and m.sale_line_id
        )
        for move in moves:
            sale_line = move.sale_line_id
            product_cost = move._get_price_unit()
            if (
                sale_line.product_uom_id
                and sale_line.product_uom_id != move.product_id.uom_id
            ):
                product_cost = move.product_id.uom_id._compute_price(
                    product_cost,
                    sale_line.product_uom_id,
                )
            sale_line.purchase_price = product_cost
