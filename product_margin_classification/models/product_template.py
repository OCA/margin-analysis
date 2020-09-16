# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    MARGIN_STATE_SELECTION = [
        ("correct", "Correct Margin"),
        ("too_cheap", "Too Cheap"),
        ("too_expensive", "Too Expensive"),
    ]

    # Columns Section
    margin_classification_id = fields.Many2one(
        string="Margin Classification",
        related='product_variant_ids.margin_classification_id',
        readonly=False,
        comodel_name="product.margin.classification",
    )

    theoretical_price = fields.Float(
        string="Theoretical Price",
        related='product_variant_ids.theoretical_price',
        digits=dp.get_precision("Product Price"),
    )

    theoretical_difference = fields.Float(
        string="Theoretical Difference",
        related='product_variant_ids.theoretical_difference',
        digits=dp.get_precision("Product Price"),
    )

    margin_state = fields.Selection(
        string="Theoretical Price State",
        related='product_variant_ids.margin_state',
        selection=MARGIN_STATE_SELECTION,
    )

    # Custom Section
    @api.multi
    def use_theoretical_price(self):
        self.mapped("product_variant_ids").use_theoretical_price()
