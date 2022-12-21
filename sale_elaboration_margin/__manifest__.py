# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Elaboration Margin",
    "summary": "Compute elaboration margins in sale orders lines",
    "version": "15.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Sale",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_elaboration"],
    "data": ["views/sale_order_views.xml"],
}
