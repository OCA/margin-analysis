# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Margin Pricelist Computation",
    "summary": "Calculation of margins based on price lists",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_margin"],
    "data": ["views/product_pricelist_item_views.xml"],
}
