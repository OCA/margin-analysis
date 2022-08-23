# Copyright 2021 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_margin_applicable_lines(self):
        lines = super()._get_margin_applicable_lines()
        return lines.filtered(lambda x: not x.sale_line_ids.is_downpayment)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # pylint: disable=W8110
    @api.depends("purchase_price", "price_subtotal")
    def _compute_margin(self):
        for line in self:
            if any(line.sale_line_ids.mapped("is_downpayment")):
                line.update(
                    {"margin": 0.0, "margin_signed": 0.0, "margin_percent": 0.0}
                )
            else:
                super(AccountMoveLine, line)._compute_margin()
