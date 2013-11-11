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

from openerp.osv import orm, fields
import decimal_precision as dp
import logging


class Product(orm.Model):
    _inherit = 'product.product'

    #TODO : compute the margin with default taxes
    def _amount_tax_excluded(self, cr, uid, ids, context=None):
        """
        Compute the list price total without tax (in case you are in tax included).
        This will use the default taxes defined on the product.
        :return dict of values:
            {INT Product ID:
                float price without tax
            }
        """
        res = {}
        if context is None:
            context = {}
        tax_obj = self.pool.get('account.tax')
        for prod in self.browse(cr, uid, ids):
            price = prod.list_price
            taxes = tax_obj.compute_all(cr, uid, prod.taxes_id, price, 1, product=prod.id)
            res[prod.id] = taxes['total']
        return res

    def _compute_margin(self, cursor, user, ids, field_name, arg, context=None):
        """
        Calculate the margin based on product infos. Take care of the cost_field
        define in product_get_cost_field. So the margin will be computed based on this
        field.

        We don't take care of the product price type currency to remove the dependency on
        the sale module. We consider the cost and sale price is in the company currency.

        We take care of the default product taxes, and base our computation on total without
        tax.

        :return dict of dict of the form :
            {INT Product ID : {
                {'margin_absolute': float,
                 'margin_relative': float}
            }}
        """
        logger = logging.getLogger('product_standard_margin')
        if context is None:
            context = {}
        res = {}
        if not ids:
            return res
        for product in ids:
            res[product] = {'margin_absolute': 0, 'margin_relative': 0}
        for product in self.browse(cursor, user, ids):
            cost = product.cost_price
            sale = self._amount_tax_excluded(cursor, user,
                    [product.id], context=context)[product.id]
            res[product.id]['standard_margin'] = sale - cost
            if sale == 0:
                logger.debug("Sale price for product ID %d is 0, cannot compute margin rate...", product.id)
                res[product.id]['standard_margin_rate'] = 999.
            else:
                res[product.id]['standard_margin_rate'] = (sale - cost) / sale * 100
        return res

    _columns = {
        'standard_margin': fields.function(
                _compute_margin,
                method=True,
                string='Theorical Margin',
                digits_compute=dp.get_precision('Sale Price'),
                multi='margin',
                help='Theorical Margin is [ sale price (Wo Tax) - cost price ] '
                    'of the product form (not based on historical values). '
                    'Take care of tax include and exclude. If no sale price, '
                    'the margin will be negativ.'),
        'standard_margin_rate': fields.function(
                _compute_margin,
                method=True,
                string='Theorical Margin (%)',
                digits_compute=dp.get_precision('Sale Price'),
                multi='margin',
                help='Markup rate is [ Theorical Margin / sale price (Wo Tax) ] '
                    'of the product form (not based on historical values).'
                    'Take care of tax include and exclude.. If no sale price '
                    'set, will display 999.0'),
        }
