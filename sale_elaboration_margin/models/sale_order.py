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
        group_operator="avg",
    )
    elaboration_price = fields.Float(
        compute="_compute_elaboration_price",
        store=True,
        readonly=False,
        digits="Product Price",
        group_operator="avg",
    )
    elaboration_margin = fields.Monetary(
        compute="_compute_elaboration_margin",
        currency_field="currency_id",
        default=0.0,
    )

    @api.depends("elaboration_id")
    def _compute_elaboration_price(self):
        for line in self:
            if not line.elaboration_id:
                line.elaboration_cost_price = 0.0
                line.elaboration_price = 0.0
            elif line.order_id.pricelist_id and line.order_id.partner_id:
                product = line.elaboration_id.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id.id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id,
                    fiscal_position=self.env.context.get("fiscal_position"),
                )
                line.elaboration_price = self.env[
                    "account.tax"
                ]._fix_tax_included_price_company(
                    line._get_display_price(product),
                    product.taxes_id,
                    line.tax_id,
                    line.company_id,
                )
                line.elaboration_cost_price = (
                    line.elaboration_id.product_id.standard_price
                )

    def _compute_elaboration_margin(self):
        for line in self:
            line.elaboration_margin = (line.qty_delivered or line.product_uom_qty) * (
                line.elaboration_price - line.elaboration_cost_price
            )
