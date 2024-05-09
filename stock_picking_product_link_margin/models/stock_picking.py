# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_view_products(self):
        result = super().action_view_products()
        # The view is only available for product.product.
        if result["res_model"] == "product.product":
            view_id = self.env.ref(
                "product_margin_classification.view_product_product_tree"
            )
            # Theoretically this could be done with more precision. If the
            # "views" key already exists, we are only interested in modifying
            # the tree tuple. I leave this as an exercise to the bothered.
            result["views"] = [(view_id.id, "tree"), (False, "form")]
        return result
