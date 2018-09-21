# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    purchase_price = fields.Float(
        string='Purchase Price',
        readonly=True,
    )

    def _select(self):
        select_str = super(SaleReport, self)._select()
        select_str += """,
            SUM(l.purchase_price / COALESCE(cr.rate, 1.0)) as purchase_price
        """
        return select_str
