from odoo import api, models
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "reward_generated_line_ids",
        "reward_origin_generated_line_ids",
        "reward_generated_line_ids.purchase_price",
    )
    def _compute_margin(self):
        res = super()._compute_margin()
        for origin_line in self.filtered(lambda x: x.reward_generated_line_ids):
            processed_reward = set()
            calculated_margin = 0
            purchase_price_total = origin_line.purchase_price
            for reward_line in origin_line.reward_generated_line_ids:
                purchase_price_total += reward_line.purchase_price
                if (
                    not reward_line.reward_id.sale_margin_formula
                    or reward_line.reward_id.id in processed_reward
                ):
                    continue
                processed_reward.add(reward_line.reward_id.id)
                eval_context = origin_line._get_reward_eval_context(reward_line)
                safe_eval(
                    str(reward_line.reward_id.sale_margin_formula).strip(),
                    eval_context,
                    mode="exec",
                    nocopy=True,
                )
                calculated_margin += eval_context.get("result", 0)
            if calculated_margin:
                origin_line.margin = float_round(
                    calculated_margin
                    * origin_line.purchase_price
                    / purchase_price_total,
                    precision_digits=2,
                )
                margin_percent_total = calculated_margin / origin_line.price_subtotal
                origin_line.margin_percent = float_round(
                    origin_line.purchase_price
                    / purchase_price_total
                    * margin_percent_total,
                    precision_digits=2,
                )
                for reward_line in origin_line.reward_generated_line_ids.filtered(
                    lambda line: line.reward_id.sale_margin_formula
                ):
                    reward_line.margin = float_round(
                        calculated_margin
                        * reward_line.purchase_price
                        / purchase_price_total,
                        precision_digits=2,
                    )
                    reward_line.margin_percent = float_round(
                        reward_line.purchase_price
                        / purchase_price_total
                        * margin_percent_total,
                        precision_digits=2,
                    )
        return res

    def _get_reward_eval_context(self, reward_line):
        return {
            "env": self.env,
            "user": self.env.user,
            "origin_line": self,
            "reward": reward_line.reward_id,
            "reward_line": reward_line,
            "reward_lines": self.reward_generated_line_ids,
            "float_compare": float_compare,
        }
