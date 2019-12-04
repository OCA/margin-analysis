# Copyright 2017-2018 Tecnativa - Sergio Teruel
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Invoice Margin Sale",
    "summary": "Set margin in invoices from sale orders",
    "version": "12.0.1.0.0",
    "development_status": "Production/Stable",
    "maintainers": ["sergio-teruel", "carlosdauden"],
    "category": "Account",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "sale_margin",
        "account_invoice_margin",
    ],
}
