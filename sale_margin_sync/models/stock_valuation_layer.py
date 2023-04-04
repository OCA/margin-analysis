# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model_create_multi
    def create(self, vals_list):
        """Update purchase price from sale line linked to svl record"""
        svls = super().create(vals_list)
        if not self.env.context.get("skip_sale_margin_sync", False):
            svls.filtered("stock_move_id.sale_line_id").sale_margin_sync()
        return svls

    def write(self, vals):
        res = super().write(vals)
        if "unit_cost" in vals and not self.env.context.get(
            "skip_sale_margin_sync", False
        ):
            self.sale_margin_sync()
        return res

    def sale_margin_sync(self):
        """Only synchronize outgoing moves"""
        for svl in self.filtered(lambda l: (l.quantity < 0.0)):
            sale_line_id = svl.stock_move_id.sale_line_id
            product_cost = svl.unit_cost
            sale_currency = (
                sale_line_id.currency_id or sale_line_id.order_id.currency_id
            )
            if sale_line_id.product_uom and sale_line_id.product_uom != svl.uom_id:
                product_cost = svl.uom_id._compute_price(
                    product_cost,
                    sale_line_id.product_uom,
                )
            if sale_currency and product_cost and sale_currency != svl.currency_id:
                product_cost = svl.currency_id._convert(
                    from_amount=product_cost,
                    to_currency=sale_currency,
                    company=svl.company_id or self.env.company,
                    date=svl.create_date,
                    round=False,
                )
            sale_line_id.purchase_price = product_cost
