# Copyright (C) 2021 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sales Margin after other estimated costs",
    "summary": "See sales margins after other expected costs, such as shipping and delivery",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["dreispt"],
    "development_status": "Beta",
    "depends": ["sale_margin", "delivery"],
    "data": [
        "security/ir.model.access.csv",
        "views/delivery_carrier.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
