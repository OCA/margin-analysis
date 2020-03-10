# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    replenishment_cost = fields.Float(
        compute='_get_replenishment_cost_supplier_discount')

    @api.multi
    @api.depends('product_tmpl_id.seller_ids.price',
                 'product_tmpl_id.seller_ids.discount')
    def _get_replenishment_cost_supplier_discount(self):
        for product in self:
            if product.seller_ids:
                supplierinfo = product.seller_ids[0]
                product.replenishment_cost =\
                    supplierinfo.price * (1.0 - supplierinfo.discount / 100.0)
            else:
                product.replenishment_cost = 0.0
