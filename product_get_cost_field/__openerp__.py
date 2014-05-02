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
{'name' : 'Product Cost field',
 'version' : '1.0.1',
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'complexity': "normal",  # easy, normal, expert
 'depends' : [
    'product',
              ],
 'description': """
Product Cost field
==================

Provides an overridable method on product which compute the cost_price field
of a product. By default it just return the value of standard_price field, but
using the product_cost_incl_bom module, it will return the costing from the
bom.

As it is a generic module, you can also setup your own way of computing the
cost_price for your product.

All our modules to compute margin are based on it, so you'll ba able to use
them in your own way.

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>

 """,
 'website': 'http://www.camptocamp.com/',
 'data': [
    'product_view.xml'
 ],
 'demo': [],
 'test': [
    'test/cost_price_update.yml',
 ],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False
 }
