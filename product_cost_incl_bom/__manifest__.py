# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{'name' : 'Product Cost incl. BOM',
 'version' : '1.0',
 'author' : "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends' : ['product_get_cost_field',
              'mrp'],
 'description': """
Product Cost including BOM costs
================================

Compute product cost price by recursively summing parts cost prices according to product BOM. It takes into
account the BoM costing (cost per cycle and so...). If no BOM define for a product, the cost_price is always
equal to the standard_price field of the product, so we always have a value to base our reporting on.

The computed value is stored in the DB and can be used in 3rd party report.

It makes a quite complex computation to include correct computation of such use case having
such a hierarchy of products:

            - Table A
                - 2x Plank 20.-
                - 4x Wood leg 10.-
            - Table B
                - 3x Plank 20.-
                - 4x Red wood leg
            - Red wood leg
                - 1x Wood leg 10.-
                - 1x Red paint pot 10.-
            - Chair
                - 1x Plank
                - 4x Wood leg
            - Table and Chair
                - 1x Table Z
                - 4x Chair Z
Changing the price of Wood leg will update the price of Table A, Table B, Red wood leg, 
Table & Chair products.

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>

""",
 'website': 'http://www.camptocamp.com/',
 'data': [],
 'demo': [],
 'test': [
    'test/cost_price_update.yml',
    'test/cost_price_update_by_bom.yml',
    'test/cost_price_empty_phantom_bom.yml',
 ],
 'installable': False,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False}
