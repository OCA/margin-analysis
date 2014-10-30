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
{'name': 'Product Cost field',
 'version': '1.1',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Products',
 'depends': [
     'product',
     ],
 'description': """
Product Cost
============

This module brings a clear distinction between the product's value and the
cost price. The "Value" is the cost which goes in the accounting at the time
of the yearly inventory.
The "Cost Price" on the other hand is the cost that we have to support in
order to produce or acquire the goods.
Depending on your business, both prices may or may not be the same.

This module adds a new cost_price field and provides an overridable method on
product to compute it.
By default it just returns the value of the standard_price field ("Value"),
but optionally it could include the costing from the bill of materials
(see product_cost_incl_bom module).

As it is a generic module, you can also setup your own way of computing the
cost_price for your product.

All OCA modules to compute margins are based on it, so you'll be able to use
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
 'test': [
     'test/cost_price_update.yml',
     ],
 'license': 'AGPL-3',
 }
