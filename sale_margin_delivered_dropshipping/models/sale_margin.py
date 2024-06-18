# Copyright 2024 Moduon Team
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_delivered_margin_valuation_layers(self):
        """Adds Valuation Layers that involves Dropshipping and not considered
        in other scenarios."""
        valuation_layers = super()._get_delivered_margin_valuation_layers()
        for move in self.move_ids.filtered(lambda m: m.state == "done"):
            if (
                move.location_dest_usage == "customer"
                and move.location_usage == "supplier"
            ):
                # Dropship moves have 2 valuation layers. Use negative one
                valuation_layers |= move.stock_valuation_layer_ids.filtered(
                    lambda vl: vl.quantity < 0
                )
        return valuation_layers
