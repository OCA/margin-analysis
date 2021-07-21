# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    percent = fields.Float(
        string="Percent", compute="_compute_percent", digits=(16, 2),
    )

    @api.depends("margin", "amount_untaxed")
    def _compute_percent(self):
        for order in self:
            if order.margin and order.amount_untaxed:
                order.percent = (order.margin / order.amount_untaxed) * 100
            else:
                order.percent = 0.0


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_percent = fields.Float(
        string="Margin(%)", compute="_compute_margin_percent", digits=(16, 2),
    )

    @api.depends("margin", "price_subtotal")
    def _compute_margin_percent(self):
        for line in self:
            if line.margin and line.price_subtotal:
                line.margin_percent = (line.margin / line.price_subtotal) * 100
            else:
                line.margin_percent = 0.0
