# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_delivered = fields.Float(compute="_compute_margin_delivered", store=True)
    margin_delivered_percent = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
        readonly=True,
    )
    purchase_price_delivery = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
    )

    @api.depends(
        "margin",
        "qty_delivered",
        "product_uom_qty",
        "move_ids.stock_valuation_layer_ids.unit_cost",
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
                cost_price = 0.0
                moves = line.move_ids.filtered(
                    lambda x: (
                        x.state == "done"
                        and (
                            x.picking_code == "outgoing"
                            or (x.picking_code == "incoming" and x.to_refund)
                        )
                    )
                )
                for move in moves:
                    # In v12.0 price unit was negative for incomming moves, in
                    # v13.0 price unit is positive in stock valuation layer model
                    cost = move.stock_valuation_layer_ids[:1].unit_cost
                    if move.to_refund:
                        cost = -cost
                    cost_price += move.product_qty * cost
                average_price = (
                    abs(cost_price) / line.qty_delivered
                ) or line.purchase_price
                line.purchase_price_delivery = tools.float_round(
                    average_price, precision_digits=digits
                )
                line.margin_delivered = line.qty_delivered * (
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
