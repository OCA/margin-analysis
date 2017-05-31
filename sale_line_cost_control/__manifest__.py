# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{'name': 'Sales Lines Cost Control',
 'version': '10.0.1.0.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Sales',
 'depends': ['sale',
             'sale_margin',
             ],
 'website': 'https://www.camptocamp.com',
 'data': ['security/security.xml',
          'wizards/set_sale_line_purchase_price_views.xml',
          'views/sale_views.xml',
          ],
 'installable': True,
 }
