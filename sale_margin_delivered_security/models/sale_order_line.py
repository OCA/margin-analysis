# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import fields, models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "product.cost.security.mixin"]

    # Inherited fields
    purchase_price_delivery = fields.Float(
        groups="product_cost_security.group_product_cost"
    )
    margin_delivered_percent = fields.Float(
        groups="product_cost_security.group_product_cost"
    )
    margin_delivered = fields.Float(groups="product_cost_security.group_product_cost")
