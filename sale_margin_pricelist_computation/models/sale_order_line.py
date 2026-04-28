from odoo import api, models
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("pricelist_item_id", "price_unit")
    def _compute_purchase_price(self):
        for line in self.filtered(
            lambda line: line.pricelist_item_id.margin_cost_price_formula
        ):
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            eval_context = line._get_margin_pricelist_eval_context()
            safe_eval(
                str(line.pricelist_item_id.margin_cost_price_formula).strip(),
                eval_context,
                mode="exec",
                nocopy=True,
            )
            line.purchase_price = line._convert_to_sol_currency(
                eval_context.get("result", 0), line.product_id.cost_currency_id
            )
        self = self.filtered(
            lambda line: not line.pricelist_item_id.margin_cost_price_formula
        )
        return super()._compute_purchase_price()

    @api.depends("pricelist_item_id")
    def _compute_margin(self):
        self_formula = self.filtered(
            lambda line: line.pricelist_item_id.margin_sale_price_formula
        )
        for line in self_formula:
            eval_context = line._get_margin_pricelist_eval_context()
            safe_eval(
                str(line.pricelist_item_id.margin_sale_price_formula).strip(),
                eval_context,
                mode="exec",
                nocopy=True,
            )
            quantity = (
                line.qty_delivered
                if line.qty_delivered and not line.product_uom_qty
                else line.product_uom_qty
            )
            calculated_subtotal = eval_context.get("result", 0) * quantity
            line.margin = calculated_subtotal - (line.purchase_price * quantity)
            line.margin_percent = (
                calculated_subtotal and line.margin / calculated_subtotal
            )
        self -= self_formula
        return super()._compute_margin()

    def _get_margin_pricelist_eval_context(self):
        return {
            "env": self.env,
            "context": self.env.context,
            "user": self.env.user,
            "line": self,
            "pricelist": self.pricelist_item_id.pricelist_id,
            "pricelist_item": self.pricelist_item_id,
            "product": self.product_id,
            "float_compare": float_compare,
        }
