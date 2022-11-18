# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    margin = fields.Float(readonly=True)
    purchase_price = fields.Float("Cost", readonly=True)

    def _select(self):
        res = super()._select()
        outbound_types = tuple(self.env["account.move"].get_outbound_types())
        return ",\n".join(
            [
                res,
                "line.margin_signed AS margin",
                f"""
                (
                    line.purchase_price
                    * line.quantity
                    * (CASE WHEN move.move_type in {outbound_types} THEN -1 ELSE 1 END)
                ) AS purchase_price
                """,
            ]
        )
