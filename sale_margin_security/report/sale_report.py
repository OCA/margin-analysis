# Copyright 2023 Carlos Dauden - Tecnativa
# Copyright 2023 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin = fields.Float(groups="sale_margin_security.group_sale_margin_security")
