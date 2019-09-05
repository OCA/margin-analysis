# Copyright (C) 2012 - Today: Camptocamp SA
# Copyright (C) 2016 - Today: GRAP (http://www.grap.coop)
# @author: Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Replenishment Cost',
    'summary': "Provides an overridable method on product which compute"
               "the Replenishment cost of a product",
    'version': '12.0.1.0.0',
    'author': "Camptocamp,GRAP,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        'product',
    ],
    'website': 'https://github.com/OCA/margin-analysis',
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
}
