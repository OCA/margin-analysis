# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin_delivered = fields.Float(
        string='Margin Delivered',
        readonly=True,
    )

    def _select(self):
        res = super(SaleReport, self)._select()
        res += """,
            SUM(l.margin_delivered / COALESCE(cr.rate, 1.0)) as
            margin_delivered
        """
        return res
