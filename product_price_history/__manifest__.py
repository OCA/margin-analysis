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
    "name" : "Product Price History",
    "version" : "1.2.2",
    "author" : "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category" : "Generic Modules/Inventory Control",
    "depends" : ["product",
                 "purchase",
                 ],
    "description": """
Product Price History
=====================

This module allows you to:

* Record various prices of a same product for different companies. This
  way, every company can have its own costs (average or standard) and
  sale prices.
* Historize the prices in a way that you'll then be able to retrieve the
  cost (or sale) price at a given date.

Note that to benefit those values in stock report (or any other view that is based on SQL),
you'll have to adapt it to include this new historized table. Especially true for stock
valuation.

This module also contains demo data and various tests to ensure it works well. It shows
how to configure OpenERP properly when you have various company, each of them having 
their product setup in average price and using different currencies. The goal is to share
the products between all companies, keeping the right price for each of them.

As the prices are now historized, some information aren't revelant anymore in some report. This
module also hide the price information in those view to avoid having wrong informations. Instead
you'll find a view that allow you to retrive the product price and stock at a given date to value
your inventory properly.

Technically, this module updates the definition of field standard_price, list_price 
of the product and will make them stored in an external table. We override the read, 
write and create methods to achieve that and don't used ir.property for performance
and historization purpose.

You may want to also use the module analytic_multicurrency from `bzr branch lp:account-analytic/7.0`
in order to have a proper computation in analytic line as well (standard_price will be converted
in company currency with this module when computing cost of analytic line).

Contributors
------------

* Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
""",
    'demo': [
        'demo/product_price_history_purchase_demo.yml',
    ],
    'data': [
        'wizard/historic_prices_view.xml',
        'product_price_history_view.xml',
        'report_stock_view.xml',
        'security/ir.model.access.csv',
        'security/product_price_history_security.xml',
    ],
    'test': [
        'test/price_controlling_multicompany.yml',
        'test/avg_price_computation_mutlicompanies_multicurrencies.yml',
        'test/price_historization.yml',
    ],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
