# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2013 Camptocamp SA
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

from openerp.osv import orm, fields
import decimal_precision as dp
from openerp.addons.product_price_history.product_price_history import (
    PRODUCT_FIELD_HISTORIZE
)
import time
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

# Add the field cost_price to the list of historized field per company
PRODUCT_FIELD_HISTORIZE.append('cost_price')


class product_product(orm.Model):
    _inherit = 'product.product'

    def _set_field_name_values(self, cr, uid, ids, field_name, context):
        field_flag = False
        field_dict = {}
        prod_tpl_obj = self.pool.get('product.template')
        if self._log_access:
            cr.execute('select id,write_date from ' +
                       self._table + ' where id IN %s', (tuple(ids),))
            res = cr.fetchall()
            for r in res:
                if r[1]:
                    field_dict.setdefault(r[0], [])
                    res_date = time.strptime((r[1])[:19], '%Y-%m-%d %H:%M:%S')
                    write_date = datetime.fromtimestamp(time.mktime(res_date))
                    for i in self.pool._store_function.get(self._name, []):
                        if i[5]:
                            up_write_date = write_date + timedelta(hours=i[5])
                            if datetime.now() < up_write_date:
                                if i[1] in fields:
                                    field_dict[r[0]].append(i[1])
                                    if not field_flag:
                                        field_flag = True
        if self._columns[field_name]._multi:
            raise ValueError('multi is not supported on the %s field' % field_name)
        # use admin user for accessing objects having rules defined on
        # store fields
        result = self._columns[field_name].get(cr, self, ids,
                                               field_name, uid,
                                               context=context)
        for r in result.keys():
            if field_flag:
                if r in field_dict.keys():
                    if field_name in field_dict[r]:
                        result.pop(r)
        prods = self.read(cr, uid, result.keys(), ['product_tmpl_id'],
                          context=context, load='_classic_write')
        tmpls = dict((row['id'], row['product_tmpl_id']) for row in prods)
        for prod_id, value in result.iteritems():
            tmpl_id = tmpls[prod_id]
            prod_tpl_obj._log_price_change(cr, uid, tmpl_id,
                                           field_name,
                                           value,
                                           context=context)
        return True

    def _store_set_values(self, cr, uid, ids, fields, context):
        """
        Override the method to have the proper computation in case of
        cost_price history.
        Calls the fields.function's "implementation function" for all
        ``fields``, on records with ``ids`` (taking care of respecting
        ``multi`` attributes), and stores the resulting values in the
        database directly.
        """
        if not ids:
            return True
        if 'cost_price' in fields:
            fields = list(set(fields))
            fields.remove('cost_price')
            self._set_field_name_values(cr, uid, ids, 'cost_price', context)
        res = super(product_product, self)._store_set_values(cr,
                                                             uid,
                                                             ids,
                                                             fields,
                                                             context)
        return res

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        res = super(product_product, self)._cost_price(cr, uid, ids,
                                                       field_name,
                                                       arg,
                                                       context=context)
        return res

    def _get_product2(self, cr, uid, ids, context=None):
        mrp_obj = self.pool.get('mrp.bom')
        res = mrp_obj._get_product(cr, uid, ids, context=context)
        return res

    def _get_bom_product2(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        res = prod_obj._get_bom_product(cr, uid, ids, context=context)
        return res

    def _get_product_from_template2(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        return prod_obj._get_product_from_template(cr, uid,
                                                   ids,
                                                   context=context)

    def _read_flat(self, cr, uid, ids, fields,
                   context=None, load='_classic_read'):
        if context is None:
            context = {}
        if not fields:
            fields = []
        else:
            fields = fields[:]  # avoid to modify the callee's list
        if fields and not 'id' in fields:
            fields.append('id')
        pt_obj = self.pool.get('product.template')

        historized_fields = [f for f in fields if f in PRODUCT_FIELD_HISTORIZE]
        remove_tmpl_field = False
        if fields and not 'product_tmpl_id' in fields and historized_fields:
            remove_tmpl_field = True
            fields.append('product_tmpl_id')

        results = super(product_product, self)._read_flat(cr, uid, ids,
                                                          fields,
                                                          context=context,
                                                          load=load)
         # Note if fields is empty => read all, so look at history table
        if not fields or historized_fields:
            date_crit = False
            price_history = self.pool.get('product.price.history')
            company_id = pt_obj._get_transaction_company_id(cr, uid,
                                                            context=context)
            if context.get('to_date'):
                date_crit = context['to_date']
            if load == '_classic_write':
                # list of ids
                tmpl_ids = [row['product_tmpl_id'] for row in results]
            else:
                # list of (id, name)
                tmpl_ids = [row['product_tmpl_id'][0] for row in results]
            prod_prices = price_history._get_historic_price(
                cr, uid,
                tmpl_ids,
                company_id,
                datetime=date_crit,
                field_names=historized_fields or PRODUCT_FIELD_HISTORIZE,
                context=context)
            for result in results:
                if load == '_classic_write':
                    tmpl_id = result['product_tmpl_id']
                else:
                    tmpl_id = result['product_tmpl_id'][0]
                dict_value = prod_prices[tmpl_id]
                result.update(dict_value)

        if remove_tmpl_field:
            for row in results:
                # this field was not asked by the callee
                del row['product_tmpl_id']
        return results

    def _product_value(self, cr, uid, ids, field_names=None,
                       arg=False, context=None):
        """ Override the method to use cost_price instead of standard_price.
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = 0.0
        products = self.read(cr, uid, ids,
                             ['id', 'qty_available', 'cost_price'],
                             context=context)
        for product in products:
            res[product['id']] = product['qty_available'] * product['cost_price']
        return res

    # Trigger on product.product is set to None, otherwise do not trigg
    # on product creation !
    _cost_price_triggers = {
        'product.product': (_get_bom_product2, None, 10),
        'product.template': (_get_product_from_template2,
                             ['standard_price'], 10),
        'mrp.bom': (_get_product2,
                    ['bom_id',
                     'bom_lines',
                     'product_id',
                     'product_uom',
                     'product_qty',
                     'product_uos',
                     'product_uos_qty',
                     ], 10)
    }

    _columns = {
        'cost_price': fields.function(
            _cost_price,
            store=_cost_price_triggers,
            string='Cost Price (incl. BoM)',
            digits_compute=dp.get_precision('Product Price'),
            help="The cost price is the standard price or, if the product has "
                 "a bom, the sum of all standard price of its components. it "
                 "take also care of the bom costing like cost per cylce."),
        'value_available': fields.function(
            _product_value,
            type='float', digits_compute=dp.get_precision('Product Price'),
            group_operator="sum",
            string='Value',
            help="Current value of products available.\n"
                 "This is using the product historize price incl. BoM."
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children."),
        }
