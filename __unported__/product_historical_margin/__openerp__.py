# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Joel Grand-Guillaume
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
{'name' : 'Product Historical Margin',
 'version' : '0.2',
 'author' : "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Accounting & Finance',
 'complexity': "normal",  # easy, normal, expert
 'depends' : ['product_get_cost_field',
              'product_standard_margin',
              'account',
              'sale',
              ],
 'description': """
 This module will store in the invoice line all the historical informations to allow you to compute
 your margin on product. We will always work in company currency and in invoice currency (to respect the OpenERP
 philosophy, as it is done in accounting entries for example). You now have the possibility to open a list 
 view of your products and having the margin computed for a given period of time. 
 
 In the product form, you also will have a computed field that show you the info based on all invoice lines
 historic.
 
 You can use this module in conjonction with the product_cost_incl_bom one to have the right margin 
 computed from BOM costing.
 
 WARNING:
 
 1) The amount of the unit price in company currency in the invoice line is converted with the currency
 rate of the date of the creation/modification of the invoice line (not the invoice date). This choice 
 has been made mainly because the cost price of the product is known at the invoice creation, but we don't 
 have it at the date of the invoice (no historical values in the cost price...) !
 
 
 """,
 'website': 'http://www.camptocamp.com/',
 'init_xml': [],
 'update_xml': ["account_invoice_view.xml",
                "wizard/historical_margin_view.xml",
                "product_view.xml",
                ],
 'demo_xml': [],
 'test': [
    'test/basic_historical_margin.yml',
 ],
 'installable': False,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False
 }
