# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
import odoo.addons.decimal_precision as dp


class Productproduct(models.Model):
    _inherit = "product.product"

    MARGIN_STATE_SELECTION = [
        ("correct", "Correct Margin"),
        ("too_cheap", "Too Cheap"),
        ("too_expensive", "Too Expensive"),
    ]

    # Columns Section
    margin_classification_id = fields.Many2one(
        comodel_name="product.margin.classification",
        string="Margin Classification",
    )

    theoretical_price = fields.Float(
        string="Theoretical Price",
        digits=dp.get_precision("Product Price"),
        compute="_compute_theoretical_multi",
        store=True,
    )

    theoretical_difference = fields.Float(
        string="Theoretical Difference",
        digits=dp.get_precision("Product Price"),
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
    @api.depends(
        "standard_price",
        "lst_price",
        "margin_classification_id",
        "margin_classification_id.markup",
        "margin_classification_id.price_round",
        "margin_classification_id.price_surcharge",
        "taxes_id",
    )
    def _compute_theoretical_multi(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Price")

        for product in self:
            classification = product.margin_classification_id
            if classification:
                multi = (100 + classification.markup) / 100
                if product.taxes_id.filtered(
                    lambda x: x.amount_type != "percent"
                ):
                    raise ValidationError(_(
                        "Unimplemented Feature\n"
                        "The sale taxes are not correctly set for computing"
                        " prices with coefficients for the product %s"
                    )
                        % (product.name)
                    )
                for tax in product.taxes_id.filtered(
                    lambda x: x.price_include
                ):
                    multi *= (100 + tax.amount) / 100.0
                product.theoretical_price = (
                    tools.float_round(
                        product.standard_price * multi,
                        precision_rounding=classification.price_round,
                    )
                    + classification.price_surcharge
                )
            else:
                product.theoretical_price = product.lst_price
            difference = product.lst_price - product.theoretical_price
            compare = float_compare(
                difference, 0, precision_digits=precision)
            if compare < 0:
                product.margin_state = "too_cheap"
            elif compare > 0:
                product.margin_state = "too_expensive"
            else:
                product.margin_state = "correct"
            product.theoretical_difference = difference

    # Custom Section
    @api.multi
    def use_theoretical_price(self):
        for product in self:
            product.lst_price = product.theoretical_price
