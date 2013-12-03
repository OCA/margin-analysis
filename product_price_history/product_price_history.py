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
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

# All field name of product that will be historize
PRODUCT_FIELD_HISTORIZE = ['standard_price', 'list_price']

_logger = logging.getLogger(__name__)

class product_price_history(orm.Model):
    # TODO : Create good index for select

    _name = 'product.price.history'
    _order = 'datetime, company_id asc'

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
                            datetime=False, field_name=None,
                            context=None):
        """ Use SQL for performance. Return a dict like:
            {product_id:{'standard_price': Value, 'list_price': Value}}
            If no value found, return 0.0 for each field and products.
        """
        res = {}
        if not ids:
            return res
        if field_name is None:
            field_name = PRODUCT_FIELD_HISTORIZE
        if not datetime:
            datetime = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        sql_wh_clause = """SELECT DISTINCT ON (product_id, name)
            datetime, product_id, name, amount
            FROM product_price_history
            WHERE product_id IN %s
            AND datetime <= %s
            AND company_id = %s
            AND name IN %s
            ORDER BY product_id, name, datetime DESC"""
        cr.execute(sql_wh_clause, (tuple(ids), datetime,
                   company_id, tuple(field_name)))
        for id in ids:
            res[id] = dict.fromkeys(field_name, 0.0)
        result = cr.dictfetchall()
        for line in result:
            data = {line['name']: line['amount']}
            res[line['product_id']].update(data)
        _logger.debug("Result of price history is : %s, company_id: %s", res, company_id)
        return res


class product_template(orm.Model):

    _inherit = "product.template"

    def _log_price_change(self, cr, uid, product, values, context=None):
        """
        On change of price create a price_history
        :param product value of new product or product_id
        """
        price_history = self.pool.get('product.price.history')
        for field_name in PRODUCT_FIELD_HISTORIZE:
            if values.get(field_name):
                data = {
                    'product_id': product,
                    'amount': values[field_name],
                    'name': field_name,
                    'company_id': self._get_transaction_company_id(cr, uid,
                        context=context)
                    }
                price_history.create(cr, uid, data, context=context)

    def _get_transaction_company_id(self, cr, uid, context=None):
        """As it may happend that OpenERP force the uid to 1 to bypass
        rule (in function field), we may sometimes read the price of the company 
        of user id 1 instead of the good one. Because we found the real uid and company_id
        in the context in that case, I return this one. It also allow other module to 
        give the proper company_id in the context (like it's done in product_standard_margin
        for example. If company_id not in context, take the one from uid."""
        res = uid
        if context == None:
            context = {}
        if context.get('company_id'):
            res = context.get('company_id')
        else:
            user_obj = self.pool.get('res.users')
            res = user_obj.browse(cr, uid, uid, 
                context=context).company_id.id
        return res

    def create(self, cr, uid, values, context=None):
        """Add the historization at product creation."""
        res = super(product_template, self).create(cr, uid, values,
                                                   context=context)
        self._log_price_change(cr, uid, res, values, context=context)
        return res

    def read(self, cr, uid, ids, fields=None, context=None,
             load='_classic_read'):
        """Override the read to take price values from the related
        price history table."""
        if context is None:
            context = {}
        if fields:
            fields.append('id')
        results = super(product_template, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        # Note if fields is empty => read all, so look at history table
        if not fields or any([f in PRODUCT_FIELD_HISTORIZE for f in fields]):
            date_crit = False
            price_history = self.pool.get('product.price.history')
            company_id = self._get_transaction_company_id(cr, uid, context=context)
            if context.get('to_date'):
                date_crit = context['to_date']
            # if fields is empty we read all price fields
            if not fields:
                price_fields = PRODUCT_FIELD_HISTORIZE
            # Otherwise we filter on price fields asked in read
            else:
                price_fields = [f for f in PRODUCT_FIELD_HISTORIZE if f in fields]
            prod_prices = price_history._get_historic_price(cr, uid, ids,
                                                            company_id,
                                                            datetime=date_crit,
                                                            field_name=price_fields,
                                                            context=context)
            for result in results:
                dict_value = prod_prices[result['id']]
                result.update(dict_value)
        return results

    def write(self, cr, uid, ids, values, context=None):
        """Create an entry in the history table for every modified price
        of every products with current datetime (or given one in context)"""
        if any([f in PRODUCT_FIELD_HISTORIZE for f in values]):
            for product in self.browse(cr, uid, ids, context=context):
                self._log_price_change(cr, uid, product.id, values,
                                       context=context)
        return super(product_template, self).write(cr, uid, ids, values,
                                                   context=context)

    def unlink(self, cr, uid, ids, context=None):
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
