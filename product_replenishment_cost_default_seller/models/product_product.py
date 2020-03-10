# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.models import Model


class ProductProduct(Model):
    _inherit = 'product.product'

    replenishment_cost = fields.Float(
        compute='_get_replenishment_cost_default_seller')

    @api.multi
    @api.depends('product_tmpl_id.seller_ids.price')
    def _get_replenishment_cost_default_seller(self):
        for product in self:
            if product.seller_ids:
                product.replenishment_cost = product.seller_ids[0].price
            else:
                product.replenishment_cost = 0.0
