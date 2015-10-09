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
    'version': '8.0.2.0.0',
    'author': 'Camptocamp,GRAP,Odoo Community Association (OCA)',
    'category': 'Product',
    'depends': [
        'product_replenishment_cost',
        'account',
    ],
    'website': 'http://www.camptocamp.com/',
    'data': [
        'data/decimal_precision.yml',
        'views/view.xml',
    ],
    'license': 'AGPL-3',
}
