# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    purchase_price = fields.Float(string="Purchase Price", readonly=True)

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        fields.update(
            {
                "purchase_price": " ,SUM(l.purchase_price /"
                " COALESCE(s.currency_rate, 1.0))"
                "AS purchase_price"
            }
        )
        return super()._query(
            with_clause=with_clause,
            fields=fields,
            groupby=groupby,
            from_clause=from_clause,
        )
