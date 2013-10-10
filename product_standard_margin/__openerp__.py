# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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
{'name': 'Markup rate on product and sales',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Sales Management',
 'complexity': "normal",  # easy, normal, expert
 'depends': ['product_get_cost_field', 'account'],
 'description': """
  Add a field on the product form that compute the standard (or theorical) margin based on the
  current values of sale and cost price present in the product form. We take care of taxe included
  or excluded.

  It will just compute it as follow: (Sale Price without tax - Cost Price) / Sale Price without tax

  Remember that this module can be used in conjonction with product_cost_incl_bom to have the 
  cost price computed from the BOM when a product has one.

  WARNING:

  1) As this module will base his simple computation on sale and cost prices, it suppose
  you have them both in the same currency (the price type must of the same currency for both of 
  them). Remember this is the default OpenERP configuration (price type of all product price 
  fields are set as the same as the company currency). We don't take care of it cause otherwise
  we should have added a dependency on sale module.


  """,
 'website': 'http://www.camptocamp.com/',
 'init_xml': [],
 'update_xml': ['product_std_margin_view.xml'],
 'demo_xml': [],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True}


