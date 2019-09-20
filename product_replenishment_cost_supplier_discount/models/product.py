# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.one
    @api.depends('product_tmpl_id.standard_price', 'standard_price',
                 'product_tmpl_id.seller_ids.price',
                 'product_tmpl_id.seller_ids.discount')
    def _get_replenishment_cost(self):
        if self.seller_ids:
            supplierinfo = self.seller_ids[0]
            self.replenishment_cost =\
                supplierinfo.price * (1.0 - supplierinfo.discount/100.0)
        else:
            super(ProductProduct, self)._get_replenishment_cost()
