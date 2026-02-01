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
                move.picking_code == "dropship"
                and move.location_id.usage == "supplier"
                and move.location_dest_id.usage == "customer"
                and not move.to_refund
            ):
                # Forward dropship moves: collect negative VL (cost)
                valuation_layers |= move.stock_valuation_layer_ids.filtered(
                    lambda vl: vl.quantity < 0
                )
            elif (
                move.picking_code == "dropship"
                and move.location_id.usage == "customer"
                and move.location_dest_id.usage == "supplier"
                and move.to_refund
            ):
                # Return dropship moves: collect positive VL (cost reversal)
                valuation_layers |= move.stock_valuation_layer_ids.filtered(
                    lambda vl: vl.quantity > 0
                )
        return valuation_layers
