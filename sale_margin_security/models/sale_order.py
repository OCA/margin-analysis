# Copyright 2023 Carlos Dauden - Tecnativa
# Copyright 2023 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin = fields.Monetary(groups="sale_margin_security.group_sale_margin_security")
    margin_percent = fields.Float(
        groups="sale_margin_security.group_sale_margin_security"
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin = fields.Float(groups="sale_margin_security.group_sale_margin_security")
    margin_percent = fields.Float(
        groups="sale_margin_security.group_sale_margin_security"
    )
    purchase_price = fields.Float(
        groups="sale_margin_security.group_sale_margin_security"
    )
