# -*- coding: utf-8 -*-
# © 2012 Alexandre Fayolle,Yannick Vaucher,Joël Grand-Guillaume,Camptocamp
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, api
from openerp.models import Model

import openerp.addons.decimal_precision as dp


class ProductProduct(Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('product_tmpl_id.standard_price')
    def _compute_replenishment_cost(self):
        for product in self:
            product.replenishment_cost = product.standard_price

    replenishment_cost = fields.Float(
        compute='_compute_replenishment_cost',
        digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")
