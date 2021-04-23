# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Repair Margin",
    "summary": "Show margin in repairs",
    "version": "12.0.1.0.0",
    "category": "Account",
    "website": "https://www.github.com/OCA/margin-analysis",
    "author": "Tecnativa, "
              "GRAP, "
              "Sergio Corato, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["sergiocorato"],
    "application": False,
    "installable": True,
    "depends": [
        "repair",
    ],
    "data": [
        "security/repair_margin_security.xml",
        "views/repair_margin_view.xml",
    ],
}
