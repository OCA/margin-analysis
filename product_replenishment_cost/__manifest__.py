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
{
    'name': 'Replenishment Cost',
    'version': '10.0.1.0.0',
    'author': "Camptocamp,GRAP,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        'product',
        'sales_team',
    ],
    'description': """
Provides an overridable method on product which compute the Replenishment cost
of a product. By default it just returns the value of "Cost price" field, but
using the product_cost_incl_bom module, it will return the costing from the
bom.

As it is a generic module, you can also setup your own way of computing the
replenishment_cost for your product.

All OCA modules to compute margins are based on it, so you'll be able to use
them in your own way.
""",
    'website': 'https://github.com/OCA/margin-analysis',
    'data': [
        'views/product_view.xml',
        'demo/res_groups.xml',
    ],
    'test': [
        'test/cost_price_update.yml',
    ],
    'installable': True,
}
