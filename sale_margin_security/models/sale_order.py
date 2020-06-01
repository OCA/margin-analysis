# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        """In sale_margin, when the line already exists, the purchase_price
           is computed with the product onchange method, so if the user doesn't
           have the field available in the view it's not going to get the right
           price. This should be fixed in v13 with the new compute fields
           possibilities.
           """
        # TODO: Check if this can be done through computed writable field
        res = super().write(vals)
        if not vals.get("product_id") or "purchase_price" in vals:
            return res
        for line in self:
            line.purchase_price = self._compute_margin(
                line.order_id, line.product_id, line.product_uom
            )
        return res
