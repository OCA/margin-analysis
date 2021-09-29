# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id", "product_uom")
    def product_id_change_margin(self):
        """Action bom cost computes the standard price from the BoM components.
        We reproduce here the condition that makes the manual action visible
        or not in the product form to trigger it automaticaly."""
        if (
            self.product_id and self.product_id.bom_count
            and self.product_id.valuation != "real_time"
        ):
            product = self.product_id.with_context(
                force_company=self.order_id.company_id.id
            ).sudo()
            product.write({"standard_price": product._get_price_from_bom()})
        return super().product_id_change_margin()
