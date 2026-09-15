# Copyright 2023 Carlos Dauden - Tecnativa
# Copyright 2023 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleReport(models.Model):
    _name = "sale.report"
    _inherit = ["sale.report", "product.cost.security.mixin"]

    margin = fields.Float(groups="product_cost_security.group_product_cost")
