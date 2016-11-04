# -*- coding: utf-8 -*-
# © 2012 Alexandre Fayolle,Yannick Vaucher,Joël Grand-Guillaume,Camptocamp
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Product Cost incl. BOM',
 'version': '8.0.1.0.0',
 'author': "Camptocamp,Sodexis,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'depends': ['product_replenishment_cost',
             'mrp'],
 'website': 'http://www.camptocamp.com/',
 'test': [
     'test/cost_price_update.yml',
     'test/cost_price_update_by_bom.yml',
     'test/cost_price_empty_phantom_bom.yml',
 ],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False}
