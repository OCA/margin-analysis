# Copyright 2021 Tecnativa - Sergio Teruel
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    elaboration_cost_price = fields.Float(
        compute="_compute_elaboration_price",
        store=True,
        readonly=False,
        string="Elaboration Cost",
        digits="Product Price",
        aggregator="avg",
    )
    elaboration_price = fields.Float(
        compute="_compute_elaboration_price",
        store=True,
        readonly=False,
        digits="Product Price",
        aggregator="avg",
    )
    elaboration_margin = fields.Monetary(
        compute="_compute_elaboration_margin",
        currency_field="currency_id",
        default=0.0,
    )

    @api.depends("elaboration_ids")
    def _compute_elaboration_price(self):
        for line in self:
            if not line.elaboration_ids:
                line.elaboration_cost_price = 0.0
                line.elaboration_price = 0.0
            elif line.order_id.pricelist_id and line.order_id.partner_id:
                elaboration_price = 0
                elaboration_cost_price = 0
                for elaboration_product in line.elaboration_ids.product_id:
                    new_sol = self.env["sale.order.line"].new(
                        {
                            "order_id": line.order_id.id,
                            "product_id": elaboration_product.id,
                            "product_uom_qty": line.product_uom_qty,
                            "product_uom": line.product_uom.id,
                            "sequence": max(
                                line.order_id.order_line.mapped("sequence"), default=0
                            )
                            + 1,
                        }
                    )
                    new_sol._compute_price_unit()
                    elaboration_price += self.env[
                        "account.tax"
                    ]._fix_tax_included_price_company(
                        new_sol.price_unit,
                        elaboration_product.taxes_id,
                        line.tax_id,
                        line.company_id,
                    )
                    new_sol.order_id = False
                    elaboration_cost_price += elaboration_product.standard_price
                line.elaboration_price = elaboration_price
                line.elaboration_cost_price = elaboration_cost_price

    def _compute_elaboration_margin(self):
        for line in self:
            line.elaboration_margin = (line.qty_delivered or line.product_uom_qty) * (
                line.elaboration_price - line.elaboration_cost_price
            )
