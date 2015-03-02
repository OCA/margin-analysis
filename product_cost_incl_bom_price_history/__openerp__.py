# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright 2013 Camptocamp SA
#    Author: Joel Grand-Guillaume
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    "name": "Replenishment Cost incl. BoM and Price History",
    "version": "1.3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "category": "Generic Modules/Inventory Control",
    "depends": ["product_cost_incl_bom",
                "product_price_history",
                ],
    "description": """
Replenishment Cost incl. BoM and Price History
==============================================

This module make the glue between product_cost_incl_bom and
product_price_history and allow to have your Replenishment cost computed from
the component of the BoM, while having it also historized by company.

It display now this value for the inventory valuation provided by
product_price_history module.

Technically speaking, the way function field store the values computed for the
cost_price to store the proper value per date and company in the history table.

Contributors
------------

* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>

""",
    'demo': [
    ],
    'data': [
    ],
    'test': [
        'test/price_historization.yml',
        'test/cost_price_update.yml',
        'test/price_controlling_multicompany.yml',
        ],
    'installable': True,
    'auto_install': True,
    'active': False,
}
