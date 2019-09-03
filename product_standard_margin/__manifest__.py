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
{
    'name': 'Product Margin and Margin Rate',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp,GRAP,Odoo Community Association (OCA)',
    'description': """
Add a field on the product form that compute the standard (or theorical)
margin based on the current values of sale and replenishment cost present in
the product form. We take care of taxe included or excluded.
""",
    'category': 'Product',
    'depends': [
        'product_replenishment_cost',
        'account',
    ],
    'website': 'https://github.com/OCA/margin-analysis',
    'demo': [
        'demo/product_product.xml',
    ],
    'data': [
        'data/decimal_precision.xml',
        'views/product_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
