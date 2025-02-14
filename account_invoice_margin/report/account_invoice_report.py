# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    margin = fields.Float(readonly=True, string="Margin Analysis")

    def _select(self):
        return SQL("%s, line.margin_signed AS margin", super()._select())
