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
        "Average Unit Cost of Delivered Products)\n\nValue may differ from "
        "Cost Price because Stock Valuation Layers are used instead of Cost on line.",
    )
    margin_delivered_percent = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
        readonly=True,
        help="Margin percent between the Unit Price with discounts and "
        "Delivered Unit Cost.\n\n"
        "Formula: ((Unit Price with Discounts - Average Unit Cost of "
        "delivered products) / Unit Price with Discounts)",
    )
    purchase_price_delivery = fields.Float(
        compute="_compute_margin_delivered",
        store=True,
        help="Average Unit Cost of delivered products.\n\n"
        "Formula: Value Delivered / Quantity Delivered\n\n"
        "When using the FIFO method, the value of this field may not match the "
        "actual cost of the product delivered.\n"
        "There may also be differences with the costing of the Sales from "
        "Deliveries report, because when the sales order is created, it is not known "
        "exactly which units will actually be delivered to calculate their cost.\n"
        "This is because when the sales order is created, it is not known which "
        "units will actually be delivered to calculate their actual cost. You do not "
        "have this information until you validate the corresponding delivery note.",
    )

    def _get_delivered_margin_valuation_layers(self):
        """Gets all Valuation Layers that should be considered for
        Delivered Margin calculation."""
        self.ensure_one()
        valuation_layers = self.env["stock.valuation.layer"]
        for move in self.move_ids.filtered(lambda m: m.state == "done"):
            if move.picking_code == "outgoing":
                # Outgoing moves have 1 valuation layer and are always negative
                valuation_layers |= move.stock_valuation_layer_ids
            elif move.picking_code == "incoming" and move.to_refund:
                # Incoming moves have 2 valuation layers. Use positive one
                valuation_layers |= move.stock_valuation_layer_ids.filtered(
                    lambda vl: vl.quantity > 0
                )
        return valuation_layers

    @api.depends(
        "margin",
        "qty_delivered",
        "product_uom_qty",
        "move_ids.stock_valuation_layer_ids.value",
        "move_ids.stock_valuation_layer_ids.quantity",
    )
    def _compute_margin_delivered(self):
        """Computes the Delivered Margin of the Lines.

        It is calculated based on the Valuation Layers of each Line.
        """
        digits = self.env["decimal.precision"].precision_get("Product Price")
        self.margin_delivered = 0.0
        self.margin_delivered_percent = 0.0
        self.purchase_price_delivery = 0.0
        for line in self.filtered("qty_delivered"):
            # we need to compute the price reduce to avoid rounding issues
            # the one stored in the line is rounded to the product price precision
            price_reduce_taxexcl = (
                line.price_subtotal / line.product_uom_qty
                if line.product_uom_qty
                else 0.0
            )

            if not line.product_id.is_storable:
                currency = (
                    line.order_id.pricelist_id.currency_id
                    or line.company_id.currency_id
                )
                price = line.purchase_price
                line.margin_delivered = currency.round(
                    line.price_subtotal - (price * line.qty_delivered)
                )
                line.purchase_price_delivery = price
            else:
                valuation_layers = line._get_delivered_margin_valuation_layers()
                value_delivered = sum(valuation_layers.mapped("value"))
                qty_delivered = (
                    sum(
                        vl.uom_id._compute_quantity(vl.quantity, line.product_uom)
                        for vl in valuation_layers
                    )
                    or -line.qty_delivered
                )
                # purchase_price_delivery always will be positive
                # because division of same signs
                line.purchase_price_delivery = tools.float_round(
                    value_delivered / qty_delivered, precision_digits=digits
                )
                # Inverse qty_delivered because outgoing quantities are negative
                line.margin_delivered = -qty_delivered * (
                    price_reduce_taxexcl - line.purchase_price_delivery
                )
            # compute percent margin based on delivered quantities or ordered
            # quantities
            if price_reduce_taxexcl:
                line.margin_delivered_percent = (
                    price_reduce_taxexcl - line.purchase_price_delivery
                ) / price_reduce_taxexcl
