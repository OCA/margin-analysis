# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin_delivered = fields.Float(readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["margin_delivered"] = f"""SUM(l.margin_delivered
            / {self._case_value_or_one('s.currency_rate')}
            * {self._case_value_or_one('account_currency_table.rate')})
        """
        return res
