# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    purchase_price = fields.Float(groups="product_cost_security.group_product_cost")
    margin_percent = fields.Float(groups="product_cost_security.group_product_cost")
