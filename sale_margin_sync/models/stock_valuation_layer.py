# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    def write(self, vals):
        res = super().write(vals)
        if "unit_cost" in vals and not self.env.context.get(
            "skip_sale_margin_sync", False
        ):
            self.sale_margin_sync()
        return res

    def sale_margin_sync(self):
        for svl in self.filtered(lambda l: (l.quantity < 0.0)):
            svl.stock_move_id.sale_line_id.purchase_price = svl.unit_cost
