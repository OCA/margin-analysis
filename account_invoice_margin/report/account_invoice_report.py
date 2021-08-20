# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        res = super(AccountInvoiceReport, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        if "margin" not in fields:
            return res

        full_fields = all(
            x in fields
            for x in {"margin", "margin_percent"}
        )
        margin_percent = "margin_percent" in fields
        for line in res:
            if full_fields:  # compute difference
                line["margin_percent"] = ((line["margin"] or 0.0) / line[
                    "price_total"
                ]) * 100
            elif margin_percent:  # Remove wrong 0 values
                del line["margin_percent"]
        return res
