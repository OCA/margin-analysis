# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Joel Grand-Guillaume
#    Copyright 2013 Camptocamp SA
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
{'name' : 'Product Cost field Report',
 'version' : '1.0',
 'author' : "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends' : [
        'product_get_cost_field',
        'stock',
              ],
 'description': """
Product Cost field Report
=========================

This module override the reporting view of OpenERP to replace the standard_price field used
by the new cost_price one. This way all reporting of OpenERP will now take this field into 
account and display the correct result.

We're talking here about the reporting found under : Reporting -> Warehouse

Contributors
------------

* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>

 """,
 'website': 'http://www.camptocamp.com/',
 'data': [
    'product_stock_view.xml',
 ],
 'demo': [],
 'test': [],
 'installable': False,
 'auto_install': True,
 'license': 'AGPL-3',
 'application': False
 }
