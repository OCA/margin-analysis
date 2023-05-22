# Copyright 2021 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_margin_applicable_lines(self):
        invoice_lines = super()._get_margin_applicable_lines()
        return invoice_lines.filtered(
            lambda x: not any(x.sale_line_ids.mapped("is_downpayment"))
        )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # pylint: disable=W8110
    @api.depends("purchase_price", "price_subtotal")
    def _compute_margin(self):
        invoice_lines_with_downpayment = self.filtered(
            lambda x: any(x.sale_line_ids.mapped("is_downpayment"))
        )
        invoice_lines_with_downpayment.update(
            {
                "margin": 0.0,
                "margin_signed": 0.0,
                "margin_percent": 0.0,
            }
        )
        super(AccountMoveLine, self - invoice_lines_with_downpayment)._compute_margin()
