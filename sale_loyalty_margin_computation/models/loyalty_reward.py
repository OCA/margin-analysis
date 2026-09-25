# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    @api.constrains("sale_margin_formula")
    def _check_sale_margin_formula(self):
        res = super()._check_sale_margin_formula()
        main_product = self.env["product.product"].new(
            {
                "name": "Main Product",
                "list_price": 35.0,
                "standard_price": 11.52,
            }
        )
        order = self.env["sale.order"].new(
            {
                "partner_id": self.env.ref("base.partner_admin").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": main_product.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 35.0,
                        }
                    )
                ],
            }
        )
        fake_eval_context = {
            "env": self.env,
            "user": self.env.user,
            "origin_line": order.order_line[0],
            "reward_line": order.order_line[0],
            "reward_lines": order.order_line,
            "float_compare": float_compare,
        }
        for reward in self:
            if not reward.sale_margin_formula:
                continue
            fake_eval_context.update({"reward": reward})
            try:
                safe_eval(
                    str(reward.sale_margin_formula).strip(),
                    fake_eval_context,
                    mode="exec",
                    nocopy=True,
                )
            except Exception as e:
                raise ValidationError(
                    self.env._("Invalid sale margin formula:\n%(error)s", error=e)
                ) from e
        return res
