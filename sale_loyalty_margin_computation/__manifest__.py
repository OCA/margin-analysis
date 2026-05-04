# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Loyalty Margin Computation",
    "summary": "Allows to use a formula from reward for calculate sale margin",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "loyalty_margin_computation",
        "sale_loyalty_order_line_link",
        "sale_loyalty_multi_gift",
        "sale_margin_pricelist_computation",
    ],
    "data": [
        "views/loyalty_reward_views.xml",
    ],
}
