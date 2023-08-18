# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from .product_product import MARGIN_STATE_SELECTION


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Columns Section
    margin_classification_id = fields.Many2one(
        string="Margin Classification",
        compute="_compute_theoretical_multi_template",
        inverse="_inverse_margin_classification_id",
        comodel_name="product.margin.classification",
    )

    theoretical_price = fields.Float(
        compute="_compute_theoretical_multi_template",
        digits="Product Price",
    )

    theoretical_difference = fields.Float(
        compute="_compute_theoretical_multi_template",
        digits="Product Price",
    )

    margin_state = fields.Selection(
        string="Theoretical Price State",
        compute="_compute_theoretical_multi_template",
        selection=MARGIN_STATE_SELECTION,
    )

    def _get_related_fields_variant_template(self):
        res = super()._get_related_fields_variant_template()
        res.append("margin_classification_id")
        return res

    @api.onchange(
        "standard_price", "taxes_id", "margin_classification_id", "list_price"
    )
    def _onchange_standard_price(self):
        (
            self.margin_state,
            self.theoretical_price,
            self.theoretical_difference,
        ) = self.env["product.product"]._get_margin_info(
            self.margin_classification_id,
            self.taxes_id,
            self.name,
            self.standard_price,
            self.list_price,
        )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.margin_classification_id",
        "product_variant_ids.theoretical_price",
        "product_variant_ids.theoretical_difference",
        "product_variant_ids.margin_state",
    )
    def _compute_theoretical_multi_template(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            variant = template.product_variant_ids[0]
            template.margin_classification_id = variant.margin_classification_id
            template.theoretical_price = variant.theoretical_price
            template.theoretical_difference = variant.theoretical_difference
            template.margin_state = variant.margin_state
        for template in self - unique_variants:
            template.margin_classification_id = 0.0
            template.theoretical_price = 0.0
            template.theoretical_difference = 0.0
            template.margin_state = 0.0

    def _inverse_margin_classification_id(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.margin_classification_id = (
                    template.margin_classification_id
                )

    # Custom Section
    def use_theoretical_price(self):
        self.mapped("product_variant_ids").use_theoretical_price()
