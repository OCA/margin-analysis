# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    sales_margin = fields.Float(compute="_compute_product_margin_fields_values")
    sales_margin_rate = fields.Float(compute="_compute_product_margin_fields_values")

    def _compute_product_margin_fields_values(self):
        res = super()._compute_product_margin_fields_values()
        for product in self:
            product_values = res[product.id]
            product_values["sales_margin"] = product_values["turnover"] - (
                product_values["sale_num_invoiced"]
                * product_values["purchase_avg_price"]
            )
            product_values["sales_margin_rate"] = (
                product_values["sales_margin"] * 100
            ) / (product_values["turnover"] or 1)
            product.update(res[product.id])
        return res
