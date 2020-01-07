# Copyright (C) 2012 - Today: Camptocamp SA
# @author: Joel Grand-Guillaume
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Column Section
    list_price_vat_excl = fields.Float(
        compute="_compute_margin",
        string="Sale Price VAT Excluded",
        digits=dp.get_precision("Product Price"),
    )

    standard_margin = fields.Float(
        compute="_compute_margin",
        string="Theorical Margin",
        digits=dp.get_precision("Product Price"),
        help="Theorical Margin is [ sale price (Wo Tax) - cost price ] "
        "of the product form (not based on historical values). "
        "Take care of tax include and exclude. If no sale price, "
        "the margin will be negativ.",
    )

    standard_margin_rate = fields.Float(
        compute="_compute_margin",
        string="Theorical Margin (%)",
        digits=dp.get_precision("Product Price"),
        help="Margin rate is [ Theorical Margin / sale price (Wo Tax) ] "
        "of the product form (not based on historical values)."
        "Take care of tax include and exclude.. If no sale price "
        "set, will display 999.0",
    )

    # Compute Section
    @api.depends(
        "lst_price",
        "standard_price",
        "taxes_id.price_include",
        "taxes_id.amount",
        "taxes_id.include_base_amount",
    )
    def _compute_margin(self):
        # The code is duplicated from product.product model
        # because otherwise, the recomputation is not done correctly
        # when the product datas are changed from the template view
        for template in self:
            template.list_price_vat_excl = template.taxes_id.compute_all(
                template.list_price, product=template
            )["total_excluded"]
            template.standard_margin = (
                template.list_price_vat_excl - template.standard_price
            )
            if template.list_price_vat_excl == 0:
                template.standard_margin_rate = 999.0
            else:
                template.standard_margin_rate = (
                    (template.list_price_vat_excl - template.standard_price)
                    / template.list_price_vat_excl
                    * 100
                )
