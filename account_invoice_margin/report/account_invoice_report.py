# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    margin = fields.Float(readonly=True, string="Margin Analysis")

    def _select_list(self, table):
        return [*super()._select_list(table), SQL("%s AS margin", table.margin_signed)]
