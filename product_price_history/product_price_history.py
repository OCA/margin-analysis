# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright 2013 Camptocamp SA
#    Author: Joel Grand-Guillaume
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging
import time
from openerp.osv import orm, fields, expression
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

# All field name of product that will be historize
PRODUCT_FIELD_HISTORIZE = ['standard_price', 'list_price']

_logger = logging.getLogger(__name__)


class product_price_history(orm.Model):
    _name = 'product.price.history'
    _order = 'datetime, company_id asc'

    def _auto_init(self, cr, context=None):
        res = super(product_price_history, self)._auto_init(cr,
                                                            context=context)
        cr.execute("SELECT indexname "
                   "FROM pg_indexes "
                   "WHERE indexname = 'product_price_history_all_index'")
        if not cr.fetchone():
            cr.execute("CREATE INDEX product_price_history_all_index "
                       "ON product_price_history "
                       "(product_id, company_id, name, datetime)")
        return res

    _columns = {
        'name': fields.char('Field name', size=32, required=True),
        'company_id': fields.many2one('res.company', 'Company',
                                      required=True),
        'product_id': fields.many2one('product.template', 'Product',
                                      required=True),
        'datetime': fields.datetime('Date'),
        'amount': fields.float('Amount',
                               digits_compute=dp.get_precision('Product Price')),
    }

    def _get_default_company(self, cr, uid, context=None):
        company = self.pool.get('res.company')
        return company._company_default_get(cr, uid,
                                            'product.template',
                                            context=context)

    def _get_default_date(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('to_date'):
            result = context.get('to_date')
        else:
            result = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return result

    _defaults = {
        'company_id': _get_default_company,
        'datetime': _get_default_date,
    }

    def _get_historic_price(self, cr, uid, ids, company_id,
                            datetime=False, field_names=None,
                            context=None):
        """ Use SQL for performance. Return a dict like:
            {product_id:{'standard_price': Value, 'list_price': Value}}
            If no value found, return 0.0 for each field and products.
        """
        res = {}
        if not ids:
            return res
        if field_names is None:
            field_names = PRODUCT_FIELD_HISTORIZE
        if not datetime:
            datetime = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        select = ("SELECT DISTINCT ON (product_id, name) "
                  "datetime, product_id, name, amount ")
        table = "FROM product_price_history "
        where = ("WHERE product_id IN %s "
                 "AND company_id = %s "
                 "AND name IN %s "
                 "AND datetime <= %s ")
        args = [tuple(ids), company_id, tuple(field_names), datetime]
        # at end, sort by ID desc if several entries are created
        # on the same datetime
        order = ("ORDER BY product_id, name, datetime DESC, id DESC ")
        cr.execute(select + table + where + order, args)
        for id in ids:
            res[id] = dict.fromkeys(field_names, 0.0)
        result = cr.dictfetchall()
        for line in result:
            data = {line['name']: line['amount']}
            res[line['product_id']].update(data)
        _logger.debug("Result of price history is : %s, company_id: %s",
                      res, company_id)
        return res


class product_product(orm.Model):
    _inherit = "product.product"

    def _product_value(self, cr, uid, ids,
                       field_names=None, arg=False, context=None):
        """ Comute the value of product using qty_available and historize
        values for the price.
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = 0.0
        products = self.read(cr, uid, ids,
                             ['id', 'qty_available', 'standard_price'],
                             context=context)
        _logger.debug("product value get, result :%s, context: %s",
                      products, context)
        for product in products:
            res[product['id']] = product['qty_available'] * product['standard_price']
        return res

    _columns = {
        'value_available': fields.function(
            _product_value,
            type='float', digits_compute=dp.get_precision('Product Price'),
            group_operator="sum",
            string='Value',
            help="Current value of products available.\n"
                 "This is using the product historize price."
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children."),
    }

    def open_product_historic_prices(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        prod_tpl_obj = self.pool.get('product.template')
        prod_tpl_ids = []
        for product in self.browse(cr, uid, ids, context=context):
            if product.product_tmpl_id.id not in prod_tpl_ids:
                prod_tpl_ids.append(product.product_tmpl_id.id)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 
            'product_price_history', 'action_price_history', context=context)
        res['domain'] = expression.AND([res.get('domain', []), 
            [('product_id', 'in', prod_tpl_ids)]])
        return res

class product_template(orm.Model):
    _inherit = "product.template"

    def _log_all_price_changes(self, cr, uid, product, values, context=None):
        """
        For each field to historize, call the _log_price_change method
        @param: values dict of vals used by write and create od product
        @param: int product ID
        """
        for field_name in PRODUCT_FIELD_HISTORIZE:
            if values.get(field_name):
                amount = values[field_name]
                self._log_price_change(cr, uid, product, field_name,
                                       amount, context=context)
        return True

    def _log_price_change(self, cr, uid, product, field_name, amount, context=None):
        """
        On change of price create a price_history
        :param int product value of new product or product_id
        """
        res = True
        price_history = self.pool.get('product.price.history')
        company = self._get_transaction_company_id(cr, uid,
                                                   context=context)
        data = {
            'product_id': product,
            'amount': amount,
            'name': field_name,
            'company_id': company
        }
        p_prices = price_history._get_historic_price(cr, uid, [product],
                                                     company,
                                                     field_names=[field_name],
                                                     context=context)

        if p_prices[product].get(field_name) != amount:
            _logger.debug("Log price change (product id: %s): %s, field: %s",
                          product, amount, field_name)
            res = price_history.create(cr, uid, data, context=context)
        return res

    def _get_transaction_company_id(self, cr, uid, context=None):
        """
        As it may happend that OpenERP force the uid to 1 to bypass
        rule (in function field), we may sometimes read the price of the company
        of user id 1 instead of the good one. Because we found the real uid
        and company_id in the context in that case, I return this one. It also
        allow other module to give the proper company_id in the context
        (like it's done in product_standard_margin for example).
        If company_id not in context, take the one from uid.
        """
        res = uid
        if context is None:
            context = {}
        if context.get('company_id'):
            res = context.get('company_id')
        else:
            user_obj = self.pool.get('res.users')
            res = user_obj.read(cr, uid, uid,
                                ['company_id'],
                                context=context)['company_id'][0]
        return res

    def create(self, cr, uid, values, context=None):
        """Add the historization at product creation."""
        res = super(product_template, self).create(cr, uid, values,
                                                   context=context)
        self._log_all_price_changes(cr, uid, res, values, context=context)
        return res

    def _read_flat(self, cr, uid, ids, fields,
                   context=None, load='_classic_read'):
        if context is None:
            context = {}
        if fields:
            fields.append('id')
        results = super(product_template, self)._read_flat(cr, uid, ids,
                                                           fields,
                                                           context=context,
                                                           load=load)
         # Note if fields is empty => read all, so look at history table
        if not fields or any([f in PRODUCT_FIELD_HISTORIZE for f in fields]):
            date_crit = False
            p_history = self.pool.get('product.price.history')
            company_id = self._get_transaction_company_id(cr, uid,
                                                          context=context)
            if context.get('to_date'):
                date_crit = context['to_date']
            # if fields is empty we read all price fields
            if not fields:
                p_fields = PRODUCT_FIELD_HISTORIZE
            # Otherwise we filter on price fields asked in read
            else:
                p_fields = [f for f in PRODUCT_FIELD_HISTORIZE if f in fields]
            prod_prices = p_history._get_historic_price(cr, uid, ids,
                                                        company_id,
                                                        datetime=date_crit,
                                                        field_names=p_fields,
                                                        context=context)
            for result in results:
                dict_value = prod_prices[result['id']]
                result.update(dict_value)

        return results

    def write(self, cr, uid, ids, values, context=None):
        """
        Create an entry in the history table for every modified price
        of every products with current datetime (or given one in context)
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        if any([f in PRODUCT_FIELD_HISTORIZE for f in values]):
            for id in ids:
                self._log_all_price_changes(cr, uid, id, values,
                                            context=context)
        return super(product_template, self).write(cr, uid, ids, values,
                                                   context=context)

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        price_history = self.pool.get('product.price.history')
        history_ids = price_history.search(cr, uid,
                                           [('product_id', 'in', ids)],
                                           context=context)
        price_history.unlink(cr, uid, history_ids, context=context)
        res = super(product_template, self).unlink(cr, uid, ids,
                                                   context=context)
        return res


class price_type(orm.Model):
    """
        The price type is used to points which field in the product form
        is a price and in which currency is this price expressed.
        Here, we add the company field to allow having various price type for
        various company, may be even in different currency.
    """
    _inherit = "product.price.type"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company',
                                      required=True),
    }

    def _get_default_company(self, cr, uid, context=None):
        company = self.pool.get('res.company')
        return company._company_default_get(cr, uid,
                                            'product.price.type',
                                            context=context)
    _defaults = {
        'company_id': _get_default_company,
    }
