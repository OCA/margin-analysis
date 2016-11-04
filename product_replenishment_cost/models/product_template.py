# -*- coding: utf-8 -*-
# © 2012 Alexandre Fayolle,Yannick Vaucher,Joël Grand-Guillaume,Camptocamp
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('standard_price')
    def _compute_replenishment_cost(self):
        for template in self:
            replenishment_cost = 0.0
            variants = template.product_variant_ids
            if variants:
                variant_costs = variants.mapped('replenishment_cost')
                replenishment_cost = sum(variant_costs) / len(variant_costs)
            template.replenishment_cost = replenishment_cost

    replenishment_cost = fields.Float(
        compute='_compute_replenishment_cost',
        digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")
