# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model_create_multi
    def create(self, vals_list):
        """Update purchase price from sale line linked to svl record"""
        svls = super().create(vals_list)
        if not self.env.context.get("skip_sale_margin_sync", False):
            svls.filtered("stock_move_id.sale_line_id").sale_margin_sync()
        return svls

    def write(self, vals):
        res = super().write(vals)
        if "unit_cost" in vals and not self.env.context.get(
            "skip_sale_margin_sync", False
        ):
            self.sale_margin_sync()
        return res

    def sale_margin_sync(self):
        """Only synchronize outgoing moves"""
        for svl in self.filtered(lambda line: line.quantity < 0.0):
            sale_line_id = svl.stock_move_id.sale_line_id
            product_cost = svl.unit_cost
            if sale_line_id.product_uom and sale_line_id.product_uom != svl.uom_id:
                product_cost = svl.uom_id._compute_price(
                    product_cost,
                    sale_line_id.product_uom,
                )
            sale_line_id.purchase_price = product_cost
