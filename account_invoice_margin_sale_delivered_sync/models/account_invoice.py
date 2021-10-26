# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    purchase_price = fields.Float(
        string='Purchase Price',
        compute='_compute_purchase_price',
        store=True,
        readonly=False,
        # HACK: Allow to write this field
        # Remove in v13
        inverse=lambda self: self,
    )

    @api.depends("sale_line_ids.purchase_price_delivery")
    def _compute_purchase_price(self):
        for line in self:
            if line.invoice_type in ['out_invoice', 'out_refund']:
                line.purchase_price = (
                    line.sale_line_ids.purchase_price_delivery or
                    line.sale_line_ids.purchase_price
                )
