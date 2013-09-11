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
 'version' : '0.1',
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends' : ['product_get_cost_field', 
              'mrp'],
 'description': """
  Compute product cost price by recursively summing parts cost prices according to product BOM. It takes into
  account the BoM costing (cost per cycle and so...). If no BOM define for a product, the cost_price is always
  equal to the standard_price field of the product, so we always have a value to base our reporting on.
""",
 'website': 'http://www.camptocamp.com/',
 'init_xml': [],
 'update_xml': [],
 'demo_xml': [],
 'tests': [],
 'installable': False,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False}
