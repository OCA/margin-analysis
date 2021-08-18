# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    purchase_price = fields.Float(string="Cost Price", readonly=True)
    margin = fields.Float(string="Margin", readonly=True)

    def _select(self):
        select_str = super()._select()
        return (
            "%s, SUM(line.purchase_price) AS purchase_price, "
            "SUM(line.margin_signed) AS margin" % select_str
        )
