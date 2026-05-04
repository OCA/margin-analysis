# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    sale_margin_formula = fields.Text(
        help="This formula is used to calculate the margin"
    )

    @api.constrains("sale_margin_formula")
    def _check_sale_margin_formula(self):
        # To be extended by other modules
        for reward in self:
            if not reward.sale_margin_formula:
                continue
            try:
                compile(
                    str(reward.sale_margin_formula).strip(), "<string>", mode="exec"
                )
            except SyntaxError as e:
                raise ValidationError(f"Syntax error {e.lineno}: {e.msg}") from e
