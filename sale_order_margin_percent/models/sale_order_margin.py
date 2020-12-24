# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin_percent',
        digits=(16, 2),
        store=True,
        )

    @api.depends('margin', 'amount_untaxed')
    def _compute_margin_percent(self):
        for order in self:
            if order.margin and order.amount_untaxed:
                order.margin_percent = (order.margin / order.amount_untaxed) * 100


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin_percent',
        digits=(16, 2),
        store=True,
        )

    @api.depends('margin', 'price_subtotal')
    def _compute_margin_percent(self):
        for order in self:
            if order.margin and order.price_subtotal:
                order.margin_percent = (order.margin / order.price_subtotal) * 100
