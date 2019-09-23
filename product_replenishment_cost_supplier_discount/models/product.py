# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('product_tmpl_id.standard_price', 'standard_price',
                 'product_tmpl_id.seller_ids.price',
                 'product_tmpl_id.seller_ids.discount')
    def _get_replenishment_cost(self):
        for product in self:
            if product.seller_ids:
                supplierinfo = product.seller_ids[0]
                product.replenishment_cost =\
                    supplierinfo.price * (1.0 - supplierinfo.discount/100.0)
            else:
                super(ProductProduct, product)._get_replenishment_cost()
