# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Margin Delivered",
    "version": "12.0.1.0.0",
    "author": "Tecnativa,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/margin-analysis",
    "category": "Sales",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "sale_margin_security",
    ],
    "data": [
        "views/sale_margin_delivered_view.xml",
    ],
    "installable": True,
    "development_status": "Production/Stable",
    "maintainers": ["sergio-teruel"],
}
