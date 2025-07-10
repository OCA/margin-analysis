# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product report sale margin",
    "summary": """Add new fields for sales margin in the Product Margins report.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/margin-analysis",
    "depends": [
        "product_margin",
    ],
    "data": ["views/product_product_views.xml"],
}
