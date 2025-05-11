# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

MARGIN_STATE_SELECTION = [
    ("correct", "Correct Margin"),
    ("too_cheap", "Too Cheap"),
    ("too_expensive", "Too Expensive"),
]


class Productproduct(models.Model):
    _inherit = "product.product"

    # Columns Section
    margin_classification_id = fields.Many2one(
        comodel_name="product.margin.classification",
        string="Margin Classification",
    )

    theoretical_price = fields.Float(
        digits="Product Price",
        compute="_compute_theoretical_multi",
        store=True,
    )

    theoretical_difference = fields.Float(
        digits="Product Price",
        compute="_compute_theoretical_multi",
        store=True,
    )

    margin_state = fields.Selection(
        string="Theoretical Price State",
        selection=MARGIN_STATE_SELECTION,
        compute="_compute_theoretical_multi",
        store=True,
    )

    # Compute Section
    @api.depends_context("company")
    @api.depends(
        "standard_price",
        "lst_price",
        "margin_classification_id",
        "margin_classification_id.markup",
        "margin_classification_id.price_round",
        "margin_classification_id.price_surcharge",
        "product_tmpl_id.taxes_id",
        "product_tmpl_id.list_price",
    )
    def _compute_theoretical_multi(self):
        for product in self:
            # Handle special case where self.env.company != product.company_id
            # we switch in a new context to avoid to have a bad standard price
            product = product.with_company(product.company_id)
            (
                product.margin_state,
                product.theoretical_price,
                product.theoretical_difference,
            ) = self._get_margin_info(
                product.margin_classification_id,
                product.taxes_id,
                product.name,
                product.standard_price,
                product.lst_price,
            )

    @api.model
    def _get_margin_info(
        self, classification, sale_taxes, product_name, standard_price, sale_price
    ):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        if classification:
            multi = (100 + classification.markup) / 100
            if sale_taxes.filtered(lambda x: x.amount_type != "percent"):
                raise ValidationError(
                    _(
                        "Unimplemented Feature\n"
                        "The sale taxes are not correctly set for computing"
                        " prices with coefficients for the product %s"
                    )
                    % (product_name)
                )
            for tax in sale_taxes.filtered(lambda x: x.price_include):
                multi *= (100 + tax.amount) / 100.0
            theoretical_price = (
                tools.float_round(
                    standard_price * multi,
                    precision_rounding=classification.price_round,
                )
                + classification.price_surcharge
            )
        else:
            theoretical_price = sale_price
        difference = sale_price - theoretical_price
        compare = float_compare(difference, 0, precision_digits=precision)
        if compare < 0:
            margin_state = "too_cheap"
        elif compare > 0:
            margin_state = "too_expensive"
        else:
            margin_state = "correct"
        return (margin_state, theoretical_price, difference)

    # Custom Section
    def use_theoretical_price(self):
        for product in self:
            product.lst_price = product.theoretical_price

    def _apply_theoretical_price(self, state_list):
        products = self.filtered(lambda x: x.margin_state in state_list)
        products.use_theoretical_price()

    def apply_theoretical_price(self):
        self._apply_theoretical_price(["too_cheap", "too_expensive"])

    def apply_theoretical_price_too_cheap(self):
        self._apply_theoretical_price(["too_cheap"])

    def apply_theoretical_price_too_expensive(self):
        self._apply_theoretical_price(["too_expensive"])
