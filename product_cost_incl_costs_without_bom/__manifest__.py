# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012 Camptocamp SA
#    Copyright 2012 Endian Solutions BV
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
{'name' : 'Product Cost field',
 'version' : '0.1',
 'author' : "Grishma Shukla,Odoo Community Association (OCA)",
 'maintainer': 'Endian Solutions',
 'category': 'Products',
 'complexity': "normal",  
 'depends' : ['product_get_cost_field',
              ],
 'description': """
 This module adds an Fixed cost field to the product form. So you can calculate a costprice with added costs, without the use of a BoM.
 """,
 'website': 'www.endiansolutions.nl',
 'license': 'AGPL-3',
 'init_xml': [],
 'update_xml': ['product_view.xml'],
 'demo_xml': [],
 'tests': [],
 'installable': False,
 'application': False
 }
