# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    margin_sale_sync_invoice_posted = fields.Boolean(
        string="Sync sale delivered margin on posted invoices", default=True,
    )
