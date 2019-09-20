# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Replenishment Cost Supplier Discount',
    'version': '10.0.1.0.0',
    'author': "PlanetaTIC,Odoo Community Association (OCA)",
    'category': 'Products',
    'description': '''This module recomputes replenishment_cost
 according supplierinfo's price and supplierinfo's discount.''',
    'depends': [
        'product_replenishment_cost_default_seller',
        'product_supplierinfo_discount',
    ],
    'website': 'https://github.com/OCA/margin-analysis',
    'data': [
    ],
    'test': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_instalable': True,
}
