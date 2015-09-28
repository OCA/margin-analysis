# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Numérigraphe SARL.
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

{
    'name': 'Replenishment cost based on latest Purchase',
    'version': '1.0',
    'author': u'Numérigraphe SARL',
    'category': 'Products',
    'description': '''
Replenishment cost based on the latest Purchase Order or quotation
==================================================================

This module aims to provide real-time information for the future costing of
products, when the price of the raw materials varies very fast and in very
important proportions (i.e. agricultural goods and other raw materials traded
on the stock market.)
When such a Product is quoted for sales, it may be desirable to compute the
Replenishment cost based on the future cost of raw materials instead of the
past prices, as price changes are not predictable.

This module changes the way the Replenishment price is computed:
- if Purchase Quotations or Purchase Orders exist for this Product, the
  Replenishment cost will reflect in real time the price of the latest
  Purchase/Quotation for this Product
- otherwise the existing logic is kept untouched (by default: take the
  Cost price, or any other computation made in another module: cost of BoMs...)
''',
    'depends': [
        'product_get_cost_field',
        'purchase',
    ],
}
