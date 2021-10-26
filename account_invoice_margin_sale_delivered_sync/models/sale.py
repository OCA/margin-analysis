# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self):
        vals = super()._prepare_invoice_line()
        vals["purchase_price"] = self.purchase_price_delivery or self.purchase_price
        return vals
