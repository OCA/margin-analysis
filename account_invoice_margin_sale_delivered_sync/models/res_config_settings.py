# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    margin_sale_sync_invoice_posted = fields.Boolean(
        related="company_id.margin_sale_sync_invoice_posted", readonly=False
    )
