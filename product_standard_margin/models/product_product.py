# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 Camptocamp SA (http://www.camptocamp.com)
#    All Right Reserved
#
#    Author : Joel Grand-Guillaume
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

    @api.multi
    @api.depends(
        'product_tmpl_id.list_price', 'replenishment_cost',
        'taxes_id.amount_type', 'taxes_id.price_include', 'taxes_id.amount',
        'taxes_id.include_base_amount')
    def _get_margin(self):
        currency_obj = self.env['res.currency']

        currency = False
        currency_id = self.env.context.get('currency_id', False)
        if currency_id:
            currency = currency_obj.browse(currency_id)
        for product in self:
            product.list_price_vat_excl = product.taxes_id.compute_all(
                product.list_price, currency, product=product.id)[
                    'total_excluded']

            product.standard_margin =\
                product.list_price_vat_excl - product.replenishment_cost
            if product.list_price_vat_excl == 0:
                product.standard_margin_rate = 999.
            else:
                product.standard_margin_rate = (
                    (product.list_price_vat_excl
                        - product.replenishment_cost) /
                    product.list_price_vat_excl * 100)

    # Column Section
    list_price_vat_excl = fields.Float(
        compute='_get_margin', string='Sale Price VAT Excluded', store=True,
        digits=dp.get_precision('Product Price'),
        )

    standard_margin = fields.Float(
        compute='_get_margin', string='Margin', store=True,
        digits=dp.get_precision('Product Price'),
        help='Margin is [ sale price (Wo Tax) - cost price ] '
             'of the product form (not based on historical values). '
             'Take care of tax include and exclude. If no sale price, '
             'the margin will be negativ.')

    standard_margin_rate = fields.Float(
        compute='_get_margin', string='Margin (%)', store=True,
        digits=dp.get_precision('Product Margin Precision'),
        help='Markup rate is [ Margin / sale price (Wo Tax) ] '
             'of the product form (not based on historical values).'
             'Take care of tax include and exclude. If no sale price '
             'set, will display 999.0')


class ProductTemplate(Model):
    _inherit = 'product.template'

    standard_margin = fields.Float(
        compute='_compute_standard_margin', string='Margin',
        store=True, digits=dp.get_precision('Product Price'),
        help='Margin is [ sale price (Wo Tax) - cost price ] '
             'of the product form (not based on historical values). '
             'Take care of tax include and exclude. If no sale price, '
             'the margin will be negativ.')

    standard_margin_rate = fields.Float(
        compute='_compute_standard_margin', string='Margin (%)',
        store=True, digits=dp.get_precision('Product Price'),
        help='Markup rate is [ Margin / sale price (Wo Tax) ] '
             'of the product form (not based on historical values).'
             'Take care of tax include and exclude. If no sale price '
             'set, will display 999.0')

    @api.multi
    @api.depends('product_variant_ids', 'product_variant_ids.standard_margin')
    def _compute_standard_margin(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.standard_margin = \
                template.product_variant_ids.standard_margin
            template.standard_margin_rate = \
                template.product_variant_ids.standard_margin_rate
        for template in (self - unique_variants):
            template.standard_margin = 999.
            template.standard_margin_rate = 999.
