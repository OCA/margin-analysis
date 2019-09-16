# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, api
from odoo.models import Model

import odoo.addons.decimal_precision as dp


class ProductProduct(Model):
    _inherit = 'product.product'

    @api.one
    @api.depends('product_tmpl_id.standard_price', 'standard_price',
                 'product_tmpl_id.seller_ids.price')
    def _get_replenishment_cost(self):
        if self.seller_ids:
            self.replenishment_cost = self.seller_ids[0].price
        else:
            super(ProductProduct, self)._get_replenishment_cost()

    replenishment_cost = fields.Float(
        string='Replenishment cost', compute='_get_replenishment_cost',
        store=True, digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")
