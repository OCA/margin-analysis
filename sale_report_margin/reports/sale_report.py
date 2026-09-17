# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    purchase_price = fields.Float(readonly=True, aggregator="avg")
    margin_percent = fields.Float(string="Margin (%)", readonly=True, aggregator="avg")

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        # Unit cost, converted to the company currency like ``price_unit``.
        res["purchase_price"] = f"""AVG(l.purchase_price
            / {self._case_value_or_one("s.currency_rate")}
            * {self._case_value_or_one("account_currency_table.rate")})"""
        # Ratio of the grouped lines' margin over their untaxed total. The currency
        # conversion applied to both amounts in the report cancels out.
        res["margin_percent"] = """
            CASE WHEN SUM(l.price_subtotal) = 0 THEN 0
            ELSE SUM(l.margin) / SUM(l.price_subtotal) END"""
        return res
