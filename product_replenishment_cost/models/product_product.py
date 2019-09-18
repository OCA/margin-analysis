# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, api
from odoo.models import Model

import odoo.addons.decimal_precision as dp


class ProductProduct(Model):
    _inherit = 'product.product'

    @api.one
    @api.depends('product_tmpl_id.standard_price', 'standard_price')
    def _get_replenishment_cost(self):
        self.replenishment_cost = self.standard_price

    replenishment_cost = fields.Float(
        string='Replenishment cost', compute='_get_replenishment_cost',
        store=True, digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")


class ProductTemplate(Model):
    _inherit = 'product.template'

    replenishment_cost = fields.Float(
        string='Replenishment cost', compute='_compute_replenishment_cost',
        store=True, digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")

    @api.multi
    @api.depends('product_variant_ids',
                 'product_variant_ids.replenishment_cost')
    def _compute_replenishment_cost(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.replenishment_cost = \
                template.product_variant_ids.replenishment_cost
        for template in (self - unique_variants):
            template.replenishment_cost = 0.0
