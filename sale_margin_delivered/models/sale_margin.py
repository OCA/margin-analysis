# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo import tools


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_delivered = fields.Float(
        string='Margin Delivered',
        compute='_compute_margin_delivered',
        store=True,
    )
    margin_delivered_percent = fields.Float(
        string='Margin Delivered Percent',
        compute='_compute_margin_delivered',
        store=True,
        readonly=True,
        oldname='margin_delivered_percent',
    )
    purchase_price_delivery = fields.Float(
        string='Purchase Price Delivered',
        compute='_compute_margin_delivered',
        store=True,
    )

    @api.depends('margin', 'qty_delivered', 'product_uom_qty',
                 'move_ids.price_unit')
    def _compute_margin_delivered(self):
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for line in self.filtered('price_reduce'):
            if not line.qty_delivered and not line.product_uom_qty:
                continue
            qty = line.qty_delivered or line.product_uom_qty
            line.purchase_price_delivery = line.purchase_price
            line.margin_delivered = line.margin
            if line.qty_delivered:
                cost_price = 0.0
                moves = line.move_ids.filtered(
                    lambda x: (
                        x.state == 'done' and (
                            x.picking_code == 'outgoing' or (
                                x.picking_code == 'incoming' and x.to_refund))
                    ))
                for move in moves:
                    cost_price += move.product_qty * move.price_unit
                average_price = (abs(cost_price) /
                                 line.qty_delivered) or line.purchase_price
                line.purchase_price_delivery = tools.float_round(
                    average_price, precision_digits=digits)
                line.margin_delivered = line.qty_delivered * (
                    line.price_reduce - line.purchase_price_delivery
                )
            # compute percent margin based on delivered quantities or ordered
            # quantities
            line.margin_delivered_percent = qty and (
                (line.price_reduce - line.purchase_price_delivery) /
                line.price_reduce * 100.0) or 0.0
