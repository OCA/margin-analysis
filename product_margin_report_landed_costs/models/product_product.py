# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    accumulated_landed_costs = fields.Float(
        compute="_compute_product_margin_fields_values",
        help="Summation of all landed costs associated"
        " with the product in the filtered period.",
    )

    purchase_avg_price = fields.Float(
        help="(Total cost (Purchase) + "
        "Accumulated landed costs) / # Invoiced in Purchase",
    )

    total_margin = fields.Float(
        help="Turnover - (# Invoiced in Sale * Avg. Unit Price (Purchases))",
    )

    def _compute_product_margin_fields_values(self):
        res = super()._compute_product_margin_fields_values()
        StockValuationAdjustmentLines = self.env["stock.valuation.adjustment.lines"]
        for product in self:
            product_values = res[product.id]
            adjustment_lines = StockValuationAdjustmentLines._read_group(
                domain=[
                    ("product_id", "=", product.id),
                    ("cost_id.date", ">=", product_values["date_from"]),
                    ("cost_id.date", "<=", product_values["date_to"]),
                ],
                groupby=["product_id"],
                aggregates=["additional_landed_cost:sum"],
            )
            accumulated_landed_cost = 0
            if adjustment_lines:
                accumulated_landed_cost = (
                    adjustment_lines[0][1]
                    if adjustment_lines and adjustment_lines[0][0] == product
                    else 0
                )

            product_values["accumulated_landed_costs"] = accumulated_landed_cost
            product_values["purchase_avg_price"] = (
                (product_values["total_cost"] + accumulated_landed_cost)
                / product_values["purchase_num_invoiced"]
                if product_values["purchase_num_invoiced"] > 0
                else 0
            )
            product_values["total_margin"] = product_values["turnover"] - (
                product_values["sale_num_invoiced"]
                * product_values["purchase_avg_price"]
            )

            product.update(res[product.id])
        return res
