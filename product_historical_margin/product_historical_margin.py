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

from openerp.osv.orm import Model
from osv import fields

import decimal_precision as dp

# TODO: re-enable when the wizard is ready
## class product_product(Model):
##     _inherit = 'product_product'
##     def _compute_margin(self, cr, uid, ids, field_names,  arg, context):
##         res = {}
##         for obj in self.browse(cr, uid, ids):
##             product = obj.product_id
##             res[obj.id] = self._compute_margin2(cr, uid, product.id, obj.discount, obj.price_unit)
##         print res
##         return res
##     _columns = {
##         'margin_absolute': fields.function(_compute_margin, method=True,
##                                         readonly=True, type='float',
##                                         string='Margin (absolute)',
##                                         multi='product_historical_margin',
##                                         digits_compute=dp.get_precision('Account'),
##                                         help="The margin on the product in absolute value"),
##         'margin_relative': fields.function(_compute_margin, method=True, 
##                                         readonly=True, type='float',
##                                         string='Margin (%)',
##                                         multi='product_historical_margin',
##                                         digits_compute=dp.get_precision('Account'),
##                                         help="The margin on the product in relative value"),
##         }


class account_invoice_line(Model):
    _inherit = 'account.invoice.line'

    def _compute_margin(self, cr, uid, ids, field_names,  arg, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            product = obj.product_id
            res[obj.id] = self._compute_margin2(cr, uid, product.id, obj.discount, obj.price_unit)
        print res
        return res

    def _compute_margin2(self, cr, uid, product_id, discount, price_unit):
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        cost_price = product.cost_price
        discount = (discount or 0.) / 100.
        sale_price = price_unit * (1. - discount)
        return {'product_cost_price': cost_price,
                'margin_absolute': sale_price - cost_price,
                'margin_relative': 100. * (sale_price - cost_price) / cost_price
                }

    def product_id_change(self, cr, uid, ids, product_id, discount, price_unit, *args, **kwargs):
        result = super(account_invoice_line, self).product_id_change(cr, uid, ids, product_id,
                                                                     *args, **kwargs)
        margin_attributes = self._compute_margin2(cr, uid, product_id, discount, price_unit)
        result['value'].update(margin_attributes)
        return result

    def onchange_discount(self, cr, uid, ids, product_id, discount, price_unit, *args, **kwargs):
        print "onchange discount"
        result = {}
        margin_attributes = self._compute_margin2(cr, uid, product_id, discount, price_unit)
        result['value'] = margin_attributes
        print result
        return result

    def onchange_price_unit(self, cr, uid, ids, product_id, discount, price_unit, *args, **kwargs):
        print "onchange price unit"
        result = {}
        margin_attributes = self._compute_margin2(cr, uid, product_id, discount, price_unit)
        result['value'] = margin_attributes
        print result
        return result

    def _recalc_margin(self, cr, uid, ids, context=None):
        return ids

    _col_store = {'account.invoice.line': (_recalc_margin,
                                           ['price_unit', 'product_id', 'discount'],
                                           10)
                  }
    _columns = {
        'product_cost_price': fields.function(_compute_margin, method=True, readonly=True,type='float',
                                              string='Historical Cost Price',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Purchase Price'),
                                              help="The cost price of the product at the time of the creation of the invoice"),
        'margin_absolute': fields.function(_compute_margin, method=True,
                                        readonly=True, type='float',
                                        string='Margin (absolute)',
                                        multi='product_historical_margin',
                                        store=_col_store,
                                        digits_compute=dp.get_precision('Account'),
                                        help="The margin on the product in absolute value"),
        'margin_relative': fields.function(_compute_margin, method=True, 
                                        readonly=True, type='float',
                                        string='Margin (%)',
                                        multi='product_historical_margin',
                                        store=_col_store,
                                        digits_compute=dp.get_precision('Account'),
                                        help="The margin on the product in relative value"),
        }
