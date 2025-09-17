# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    list_price_vat_excl = fields.Float(
        groups="product_cost_security.group_product_cost"
    )

    standard_margin = fields.Float(groups="product_cost_security.group_product_cost")

    standard_margin_rate = fields.Float(
        groups="product_cost_security.group_product_cost"
    )

    standard_markup_rate = fields.Float(
        groups="product_cost_security.group_product_cost"
    )
