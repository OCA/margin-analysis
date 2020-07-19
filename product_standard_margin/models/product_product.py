# Copyright (C) 2012 - Today: Camptocamp SA
# @author: Joel Grand-Guillaume
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Column Section
    list_price_vat_excl = fields.Float(
        compute="_compute_margin",
        string="Sale Price VAT Excluded",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    standard_margin = fields.Float(
        compute="_compute_margin",
        string="Theorical Margin",
        store=True,
        digits=dp.get_precision("Product Price"),
        help="Theorical Margin is [ sale price (Wo Tax) - cost price ] "
        "of the product form (not based on historical values). "
        "Take care of tax include and exclude. If no sale price, "
        "the margin will be negativ.",
    )

    standard_margin_rate = fields.Float(
        compute="_compute_margin",
        string="Theorical Margin (%)",
        store=True,
        digits=dp.get_precision("Product Price"),
        help="Markup rate is [ Theorical Margin / sale price (Wo Tax) ] "
        "of the product form (not based on historical values)."
        "Take care of tax include and exclude.. If no sale price "
        "set, will display 999.0",
    )

    # Compute Section
    @api.depends(
        "lst_price",
        "product_tmpl_id.list_price",
        "standard_price",
        "taxes_id.price_include",
        "taxes_id.amount",
        "taxes_id.include_base_amount",
    )
    def _compute_margin(self):
        for product in self:
            product.list_price_vat_excl = product.taxes_id.compute_all(
                product.lst_price, product=product
            )["total_excluded"]
            product.standard_margin = (
                product.list_price_vat_excl - product.standard_price
            )
            if product.list_price_vat_excl == 0:
                product.standard_margin_rate = 999.0
            else:
                product.standard_margin_rate = (
                    (product.list_price_vat_excl - product.standard_price)
                    / product.list_price_vat_excl
                    * 100
                )
