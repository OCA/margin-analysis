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
import logging

from openerp.osv.orm import Model
from osv import fields

import decimal_precision as dp

# TODO: re-enable when the wizard is ready
# Don't Forget to remove supplier from the product margin computation
# And remove credit note from the computation

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
            if obj.invoice_id.currency_id is None:
                currency_id = 0
            else:
                currency_id = obj.invoice_id.currency_id.id
            res[obj.id] = self._compute_margin2(cr, uid, product.id, obj.discount, obj.price_unit,
                                                currency_id)
        return res

    def _convert_to_invoice_currency(self, cursor, user, amount, currency_id=False):
        if not currency_id:
            return amount
        currency_obj = self.pool.get('res.currency')
        user_obj = self.pool.get('res.users')
        company_currency_id = user_obj.browse(cursor, user, user).company_id.currency_id.id
        converted_price = currency_obj.compute(cursor, user, company_currency_id,
                                                             currency_id,
                                                             amount,
                                                             round=False)
        return converted_price


    def _compute_margin2(self, cr, uid, product_id, discount, price_unit, currency_id=False):
        
        if not product_id:
            return {'product_cost_price': 0.0,
                    'margin_absolute': 0.0,
                    'margin_relative': 0.0
                    }
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        cost_price = self._convert_to_invoice_currency(cr, uid, product.cost_price, currency_id)
        discount = (discount or 0.) / 100.
        sale_price = price_unit * (1. - discount)
        logger = logging.getLogger('product_historical_margin')
        if cost_price == 0:
            logger.debug("cost price for %d is 0, cannot compute margin relative", product_id)
            margin_relative = 999.
        else:
            margin_relative = 100. * (sale_price - cost_price) / cost_price
        logger.debug('product %d: cost_price = %f margin_absolute = %f, margin_relative = %f',
                    product_id, cost_price, sale_price - cost_price, margin_relative)
        return {'product_cost_price': cost_price,
                'margin_absolute': sale_price - cost_price,
                'margin_relative': margin_relative
                }

    def product_id_change(self, cr, uid, ids, product_id, uos_id, 
                qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, 
                price_unit=False, address_invoice_id=False,
                currency_id=False, discount=0, context=None, company_id=None):
                
        result = super(account_invoice_line, self).product_id_change(cr, uid, ids, product_id, uos_id, qty=qty, name=name,
                        type=type, partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, 
                        address_invoice_id=address_invoice_id, currency_id=currency_id, context=context, 
                        company_id=company_id)
        margin_attributes = self._compute_margin2(cr, uid, product_id, discount, price_unit, currency_id)
        result['value'].update(margin_attributes)
        return result

    def onchange_discount(self, cr, uid, ids, product_id, discount, price_unit, currency_id, *args, **kwargs):
        print "onchange discount"
        result = {}
        margin_attributes = self._compute_margin2(cr, uid, product_id, discount, price_unit, currency_id)
        result['value'] = margin_attributes
        print result
        return result

    def onchange_price_unit(self, cr, uid, ids, product_id, discount, price_unit, currency_id, *args, **kwargs):
        print "onchange price unit"
        result = {}
        margin_attributes = self._compute_margin2(cr, uid, product_id, discount, price_unit, currency_id)
        result['value'] = margin_attributes
        print result
        return result

    def _recalc_margin(self, cr, uid, ids, context=None):
        return ids

    def _recalc_margin_parent(self, cr, uid, ids, context=None):
        res=[]
        for inv in self.browse(cr,uid,ids):
            for line in inv.invoice_line:
                res.append(line.id)
        return res

    _col_store = {'account.invoice.line': (_recalc_margin,
                                           ['price_unit', 'product_id', 'discount'],
                                           10),
                  'account.invoice':  (_recalc_margin_parent,
                                       ['currency_id'],
                                       10),
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

# class AccountChangeCurrency(osv.osv_memory):
#     _inherit = 'account.change.currency'
#     
#     def change_currency(self, cr, uid, ids, context=None):
#         """We copy past here the original method in order to convert as well the cost price
#         in the new curreny."""
#         res = super (self,AccountChangeCurrency).change_currency(cr,uid,ids,context)
#         obj_inv = self.pool.get('account.invoice')
#         obj_inv_line = self.pool.get('account.invoice.line')
#         obj_currency = self.pool.get('res.currency')
#         if context is None:
#             context = {}
#         data = self.browse(cr, uid, ids, context=context)[0]
#         new_currency = data.currency_id.id
#         invoice = obj_inv.browse(cr, uid, context['active_id'], context=context)
#         if invoice.currency_id.id == new_currency:
#             return {}
#         rate = obj_currency.browse(cr, uid, new_currency, context=context).rate
#         for line in invoice.invoice_line:
#             new_price = 0
#             if invoice.company_id.currency_id.id == invoice.currency_id.id:
#                 new_price = line.price_unit * rate
#                 if new_price <= 0:
#                     raise osv.except_osv(_('Error'), _('New currency is not configured properly !'))
# 
#             if invoice.company_id.currency_id.id != invoice.currency_id.id and invoice.company_id.currency_id.id == new_currency:
#                 old_rate = invoice.currency_id.rate
#                 if old_rate <= 0:
#                     raise osv.except_osv(_('Error'), _('Current currency is not configured properly !'))
#                 new_price = line.price_unit / old_rate
# 
#             if invoice.company_id.currency_id.id != invoice.currency_id.id and invoice.company_id.currency_id.id != new_currency:
#                 old_rate = invoice.currency_id.rate
#                 if old_rate <= 0:
#                     raise osv.except_osv(_('Error'), _('Current currency is not configured properly !'))
#                 new_price = (line.price_unit / old_rate ) * rate
#             obj_inv_line.write(cr, uid, [line.id], {'price_unit': new_price})
#         obj_inv.write(cr, uid, [invoice.id], {'currency_id': new_currency}, context=context)
#         return {'type': 'ir.actions.act_window_close'}
