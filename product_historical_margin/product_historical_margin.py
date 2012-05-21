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

from osv.orm import Model
from osv import fields

import decimal_precision as dp

class product_product(Model):
    _inherit = 'product.product'

class account_invoice_line(Model):
    _inherit = 'account.invoice.line'

    _columns = {
        'product_cost_price': fields.float('Historical Cost Price',
                                           readonly=True,
                                           digits_compute=dp.get_precision('Purchase Price'),
                                           help="The cost price of the product at the time of the creation of the invoice"),
        'margin_absolute': fields.float('Margin (absolute)',
                                        readonly=True,
                                        digits_compute=dp.get_precision('Account'),
                                        help="The margin on the product in absolute value"),
        'margin_relative': fields.float('Margin (%)',
                                        readonly=True,
                                        digits_compute=dp.get_precision('Account'),
                                        help="The margin on the product in relative value"),
        }


    def _compute_margin(self, cr, uid, product_id, discount, price_unit):
        product = self.pool.get('product.product').browse(product_id)
        cost_price = product.cost_price
        discount = (discount or 0.) / 100.
        sale_price = price_unit * (1. - discount)
        return {'product_cost_price': cost_price,
                'margin_absolute': sale_price - cost_price,
                'margin_relative': (sale_price - cost_price) / cost_price
                }

    def product_id_change(self, cr, uid, ids, product_id, discount, price_unit, *args, **kwargs):
        result = super(account_invoice_line, self).product_id_change(cr, uid, ids, product_id,
                                                                     *args, **kwargs)
        margin_attributes = self._compute_margin(cr, uid, product_id, discount, price_unit)
        result['value'].update(margin_attributes)
        return result

    def onchange_discount(self, cr, uid, ids, product_id, discount, price_unit, *args, **kwargs):
        result = {}
        margin_attributes = self._compute_margin(cr, uid, product_id, discount, price_unit)
        result['value'] = margin_attributes
        return result

    def onchange_price_unit(self, cr, uid, ids, product_id, discount, price_unit, *args, **kwargs):
        result = {}
        margin_attributes = self._compute_margin(cr, uid, product_id, discount, price_unit)
        result['value'] = margin_attributes
        return result
