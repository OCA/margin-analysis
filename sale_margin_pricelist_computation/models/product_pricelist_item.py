from odoo import Command, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    margin_cost_price_formula = fields.Text(
        help="This formula is used to calculate the cost price "
        "for the purposes of calculating the margin"
    )
    margin_sale_price_formula = fields.Text(
        help="This formula is used to calculate the sales order price "
        "for the purposes of margin calculation"
    )

    @api.constrains("margin_sale_price_formula", "margin_cost_price_formula")
    def _check_margin_formula(self):
        for rec in self:
            if not rec.margin_cost_price_formula and rec.margin_cost_price_formula:
                continue
            if rec.margin_sale_price_formula:
                rec._eval_python_code_margin_formula(rec.margin_sale_price_formula)
            if rec.margin_cost_price_formula:
                rec._eval_python_code_margin_formula(rec.margin_cost_price_formula)

    def _eval_python_code_margin_formula(self, test_string):
        pricelist = self.env["product.pricelist"].new({"name": "Test Pricelist"})
        pricelist_item = self.env["product.pricelist.item"].new(
            {
                "pricelist_id": pricelist.id,
                "applied_on": "3_global",
                "base": "list_price",
                "compute_price": "percentage",
                "percent_price": 10,
            }
        )
        main_product = self.env["product.product"].new(
            {"name": "Main Product", "list_price": 35.0, "standard_price": 11.52}
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
                            "pricelist_item_id": pricelist_item,
                        }
                    )
                ],
            }
        )
        test_eval_context = order.order_line._get_margin_pricelist_eval_context()
        try:
            safe_eval(
                str(test_string).strip(),
                test_eval_context,
                mode="exec",
                nocopy=True,
            )
        except Exception as e:
            raise ValidationError(
                self.env._("Invalid sale margin formula:\n%(error)s", error=e)
            ) from e
