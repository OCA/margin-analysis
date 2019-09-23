# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.models import Model


class ProductProduct(Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('product_tmpl_id.standard_price', 'standard_price',
                 'product_tmpl_id.seller_ids.price')
    def _get_replenishment_cost(self):
        for product in self:
            if product.seller_ids:
                product.replenishment_cost = product.seller_ids[0].price
            else:
                super(ProductProduct, product)._get_replenishment_cost()
