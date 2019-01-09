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

    @api.depends('margin', 'qty_delivered', 'product_uom_qty')
    def _compute_margin_delivered(self):
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for line in self.filtered('price_reduce'):
            vals = {
                'margin_delivered': 0.0,
                'margin_delivered_percent': 0.0,
                'purchase_price_delivery': line.purchase_price,
            }
            delivered_qty = 0.0
            cost_price = 0.0
            moves = line.move_ids.filtered(lambda x: (
                x.state == 'done' and x.picking_code == 'outgoing'
            ))
            for move in moves:
                delivered_qty += move.product_qty
                cost_price += move.product_qty * abs(move.price_unit)
            qty = delivered_qty or line.product_uom_qty
            average_price = qty and (
                cost_price or line.purchase_price) / qty or 0.0
            vals['purchase_price_delivery'] = tools.float_round(
                average_price, precision_digits=digits)
            if line.qty_delivered == line.product_uom_qty:
                vals['margin_delivered'] = line.margin
            elif line.product_uom_qty:
                vals['margin_delivered'] = (
                    line.qty_delivered * line.margin / line.product_uom_qty)
            vals['margin_delivered_percent'] = qty and (
                (line.price_reduce - vals['purchase_price_delivery']) /
                line.price_reduce * 100.0) or 0.0
            line.update(vals)
