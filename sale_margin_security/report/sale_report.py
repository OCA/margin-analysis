from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin = fields.Float(
        groups="sale_margin_security.group_sale_margin_security",
    )
