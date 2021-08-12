# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    margin = fields.Float(string='Margin', readonly=True)
    margin_percent = fields.Float(string='Margin (%)', readonly=True)

    def _select(self):
        select_str = super()._select()
        return '%s, sub.margin, sub.margin_percent' % select_str

    def _sub_select(self):
        select_str = super()._sub_select()
        return '%s, SUM(ail.margin_signed) AS margin, ' \
               'AVG(ail.margin_percent) AS margin_percent' % select_str
