# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Margin Security",
    "version": "11.0.1.0.0",
    "author": 'Tecnativa,'
              'Odoo Community Association (OCA)',
    "website": 'https://github.com/OCA/margin-analysis',
    "category": "Sales",
    "license": "AGPL-3",
    "depends": [
        "sale_margin",
    ],
    "data": [
        'security/sale_margin_security_security.xml',
        'views/sale_margin_security_view.xml',
    ],
    'installable': True,
}
