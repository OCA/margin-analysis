# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp


class ProductMarginClassification(models.Model):
    _name = "product.margin.classification"
    _description = "Product Margin Classification"
    _order = "name"

    # Column Section
    name = fields.Char(string="Name", required=True)

    markup = fields.Float(
        string="Markup",
        required=True,
        digits=dp.get_precision("Margin Rate"),
        help="Value that help you to compute the sale price, based on your"
        " cost, as defined: Sale Price = (Cost * (100 + Markup)) / 100\n"
        "It is computed with the following formula"
        " Markup = 100 * (Sale Price - Cost) / Cost",
    )

    profit_margin = fields.Float(
        string="Profit Margin",
        compute="_compute_profit_margin",
        inverse="_inverse_profit_margin",
        digits=dp.get_precision("Margin Rate"),
        help="Also called 'Net margin' or 'Net Profit Ratio'.\n"
        "It is computed with the following formula"
        " Profit Margin = 100 * (Sale Price - Cost) / Sale Price",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda s: s._default_company_id(),
    )

    product_ids = fields.One2many(
        string="Products",
        comodel_name="product.product",
        inverse_name="margin_classification_id",
    )

    product_qty = fields.Integer(
        string="Products Quantity",
        compute="_compute_product_qty",
        store=True
    )

    product_correct_price_qty = fields.Integer(
        string="Total Products With Correct Price",
        compute="_compute_product_different_price_qty",
    )

    product_incorrect_price_qty = fields.Integer(
        string="Total Products With Incorrect Price",
        compute="_compute_product_different_price_qty",
    )

    product_too_cheap_qty = fields.Integer(
        string="Total Products Too Cheap",
        compute="_compute_product_different_price_qty",
    )

    product_too_expensive_qty = fields.Integer(
        string="Total Products Too Expensive",
        compute="_compute_product_different_price_qty",
    )

    price_round = fields.Float(
        string="Price Rounding",
        digits=dp.get_precision("Product Price"),
        default=lambda s: s._default_price_round(),
        help="Sets the price so that it is a multiple of this value.\n"
        "Rounding is applied after the margin and before the surcharge.\n"
        "To have prices that end in 9.99, set rounding 1, surcharge -0.01",
    )

    price_surcharge = fields.Float(
        string="Price Surcharge",
        digits=dp.get_precision("Product Price"),
        help="Specify the fixed amount to add or substract(if negative) to"
        " the amount calculated with the discount.",
    )

    # Default Section
    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_price_round(self):
        decimal_obj = self.env["decimal.precision"]
        return 10 ** (-decimal_obj.precision_get("Product Price"))

    # constrains Section
    @api.constrains("markup")
    def _check_markup(self):
        precision = self.env["decimal.precision"].precision_get("Margin Rate")
        for classification in self:
            if float_compare(
                    classification.markup,
                    -100,
                    precision_digits=precision) == 0:
                raise ValidationError(_("-100 is not a valid Markup."))

    @api.multi
    def _inverse_profit_margin(self):
        pass

    @api.onchange("profit_margin")
    def _onchange_profit_margin(self):
        precision = self.env["decimal.precision"].precision_get("Margin Rate")
        for classification in self:
            if float_compare(
                    classification.profit_margin,
                    100,
                    precision_digits=precision) == 0:
                raise ValidationError(_("100 is not a valid Profit Margin."))
            classification.markup = 100 * (
                classification.profit_margin
                / (100 - classification.profit_margin)
            )

    # Compute Section
    @api.depends("markup")
    def _compute_profit_margin(self):
        precision = self.env["decimal.precision"].precision_get("Margin Rate")
        for classification in self:
            if float_compare(
                    classification.markup,
                    -100,
                    precision_digits=precision) == 0:
                raise ValidationError(_("-100 is not a valid Markup."))
            classification.profit_margin = (
                1 - (1 / (classification.markup / 100 + 1))
            ) * 100

    def _compute_product_different_price_qty(self):
        for classification in self:
            product_vals = classification.product_ids.read(["margin_state"])
            classification.product_too_cheap_qty = len([
                x["id"] for x in product_vals
                if x["margin_state"] == "too_cheap"
            ])
            classification.product_too_expensive_qty = len([
                x["id"] for x in product_vals
                if x["margin_state"] == "too_expensive"
            ])
            classification.product_correct_price_qty = len([
                x["id"] for x in product_vals
                if x["margin_state"] == "correct"
            ])
            classification.product_incorrect_price_qty = (
                classification.product_too_expensive_qty
                + classification.product_too_cheap_qty
            )

    @api.depends("product_ids")
    def _compute_product_qty(self):
        for classification in self:
            classification.product_qty = len(classification.product_ids)

    # Constraint Section
    @api.constrains("price_round")
    def _check_price_round(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Price")
        for classification in self:
            if float_compare(
                    classification.price_round,
                    -100,
                    precision_digits=precision) == 0:
                raise ValidationError(_("Price Rounding can not be null."))

    # Custom Section
    @api.multi
    def _apply_theoretical_price(self, state_list):
        products = self.mapped("product_ids").filtered(
            lambda x: x.margin_state in state_list
        )
        products.use_theoretical_price()

    @api.multi
    def apply_theoretical_price(self):
        self._apply_theoretical_price(["too_cheap", "too_expensive"])

    @api.multi
    def apply_theoretical_price_too_cheap(self):
        self._apply_theoretical_price(["too_cheap"])

    @api.multi
    def apply_theoretical_price_too_expensive(self):
        self._apply_theoretical_price(["too_expensive"])
