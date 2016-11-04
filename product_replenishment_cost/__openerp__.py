# -*- coding: utf-8 -*-
# © 2012 Alexandre Fayolle,Yannick Vaucher,Joël Grand-Guillaume,Camptocamp
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Replenishment cost',
    'version': '8.0.3.0.0',
    'author': "Camptocamp,GRAP,Sodexis,Odoo Community Association (OCA)",
    'category': 'Products',
    'depends': [
        'product',
    ],
    'website': 'http://www.camptocamp.com/',
    'data': [
        'views/view.xml',
        'demo/res_groups.yml',
    ],
    'test': [
        'test/cost_price_update.yml',
    ],
    'license': 'AGPL-3',
}
