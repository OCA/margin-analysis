# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin_delivered = fields.Float(readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res[
            "margin_delivered"
        ] = "SUM(l.margin_delivered / COALESCE(s.currency_rate, 1.0))"
        return res
