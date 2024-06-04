# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_delivered = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
        help="Total Margin of all delivered products.\n\n"
        "Formula: Delivered Quantities * (Unit Price with Discounts - "
        "Average Unit Cost of Delivered Products)",
    )
    margin_delivered_percent = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
        readonly=True,
        help="Margin percent between the Unit Price with discounts and "
        "Delivered Unit Cost.\n\n"
        "Formula: (Margin Dlvd. / Unit Price with Discounts) * 100.0",
    )
    purchase_price_delivery = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
        help="Average Unit Cost of delivered products.\n\n"
        "Formula: Value Delivered / Quantity Delivered",
    )

    @api.depends(
        "margin",
        "qty_delivered",
        "product_uom_qty",
        "move_ids.stock_valuation_layer_ids.value",
        "move_ids.stock_valuation_layer_ids.quantity",
    )
    def _compute_margin_delivered(self):
        digits = self.env["decimal.precision"].precision_get("Product Price")
        self.margin_delivered = 0.0
        self.margin_delivered_percent = 0.0
        self.purchase_price_delivery = 0.0
        for line in self.filtered("qty_delivered"):
            if line.product_id.type != "product":
                currency = line.order_id.pricelist_id.currency_id
                price = line.purchase_price
                line.margin_delivered = currency.round(
                    line.price_subtotal - (price * line.qty_delivered)
                )
                line.purchase_price_delivery = price
                continue
            else:
                moves = line.move_ids.filtered(
                    lambda x: (
                        x.state == "done"
                        and (
                            x.picking_code == "outgoing"
                            or (x.picking_code == "incoming" and x.to_refund)
                        )
                    )
                )
                # Qty and Value Delivered is negative when outgoing
                value_delivered = sum(moves.mapped("stock_valuation_layer_ids.value"))
                qty_delivered = (
                    sum(moves.mapped("stock_valuation_layer_ids.quantity"))
                    or -line.qty_delivered
                )
                # purchase_price_delivery always will be positive because division of same signs
                line.purchase_price_delivery = tools.float_round(
                    value_delivered / qty_delivered, precision_digits=digits
                )
                # Inverse qty_delivered because outgoing quantities are negative
                line.margin_delivered = -qty_delivered * (
                    line.price_reduce - line.purchase_price_delivery
                )
            # compute percent margin based on delivered quantities or ordered
            # quantities
            if line.price_reduce:
                line.margin_delivered_percent = (
                    (line.price_reduce - line.purchase_price_delivery)
                    / line.price_reduce
                    * 100.0
                )
