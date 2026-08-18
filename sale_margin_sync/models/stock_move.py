# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _set_value(self, correction_quantity=None):
        # Update purchase price from sale line linked to the move after the base
        # value is set.
        res = super()._set_value(correction_quantity=correction_quantity)
        if not self.env.context.get("skip_sale_margin_sync", False):
            self.sale_margin_sync()
        return res

    def write(self, vals):
        res = super().write(vals)
        # Update purchase price from sale line linked to the move
        if "value" in vals and not self.env.context.get("skip_sale_margin_sync", False):
            self.sale_margin_sync()
        return res

    def sale_margin_sync(self):
        """Only synchronize outgoing moves"""
        for move in self.filtered(lambda m: m._is_out() and m.sale_line_id):
            sale_line_id = move.sale_line_id
            product_cost = move._get_price_unit()
            if (
                sale_line_id.product_uom_id
                and sale_line_id.product_uom_id != move.product_id.uom_id
            ):
                product_cost = move.product_id.uom_id._compute_price(
                    product_cost,
                    sale_line_id.product_uom_id,
                )
            sale_line_id.purchase_price = product_cost
