# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Invoice Margin Sale Delivered Sync",
    "summary": "Sync invoice margin between invoices and sale orders",
    "version": "13.0.1.1.0",
    "development_status": "Beta",
    "maintainers": ["sergio-teruel"],
    "category": "Account",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_margin_delivered", "account_invoice_margin_sale"],
    "data": ["views/res_config_settings_views.xml"],
}
