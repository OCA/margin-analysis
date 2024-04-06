# Copyright 2023 Carlos Dauden - Tecnativa
# Copyright 2023 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "product.cost.security.mixin"]

    margin = fields.Monetary(groups="product_cost_security.group_product_cost")
    margin_percent = fields.Float(groups="product_cost_security.group_product_cost")


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "product.cost.security.mixin"]

    margin = fields.Float(groups="product_cost_security.group_product_cost")
    margin_percent = fields.Float(groups="product_cost_security.group_product_cost")
    purchase_price = fields.Float(groups="product_cost_security.group_product_cost")
