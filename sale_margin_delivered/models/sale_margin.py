# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.depends('margin', 'qty_delivered', 'product_uom_qty')
    def _compute_margin_delivered(self):
        for line in self.filtered('price_reduce'):
            vals = {
                'margin_delivered': 0.0,
                'margin_delivered_percent': 0.0,
            }
            if line.qty_delivered == line.product_uom_qty:
                vals['margin_delivered'] = line.margin
            elif line.product_uom_qty:
                vals['margin_delivered'] = (
                    line.qty_delivered * line.margin / line.product_uom_qty)
            vals['margin_delivered_percent'] = (
                (line.price_reduce - line.purchase_price) /
                line.price_reduce * 100.0)
            line.update(vals)
