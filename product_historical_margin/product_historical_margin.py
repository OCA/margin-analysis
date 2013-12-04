# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Joel Grand-Guillaume
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
_logger = logging.getLogger(__name__)

# Don't Forget to remove supplier (in_invoice et in_refund) from the product margin computation
# And remove out_refund from the computation
# et ne prendre que les factures paid.
class product_product(Model):
    _inherit = 'product.product'

    def _compute_margin(self, cr, uid, ids, field_names, arg, context=None):
        """
        Compute the absolute and relativ margin based on price without tax, and
        always in company currency. We exclude the (in_invoice, in_refund) from the
        computation as we only want to see in the product form the margin made on
        our sales.
        The base calculation is made from the informations stored in the invoice line
        of paid and open invoices.
        We return 999 as relativ margin if no sale price is define. We made that choice
        to differenciate the 0.0 margin from null !

        :return dict of dict of the form :
            {INT Product ID : {
                    float margin_absolute,
                    float margin_relative
                    }}
        """
        res = {}
        tot_sale = {}
        if context is None:
            context = {}
        if not ids:
            return res
        user_obj = self.pool.get('res.users')
        
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        for product_id in ids:
            res[product_id] = {'margin_absolute': 0, 'margin_relative': 0}
            tot_sale[product_id] = 0
        # get information about invoice lines relative to our products
        # belonging to open or paid invoices in the considered period
        query = '''
        SELECT product_id, type,
              SUM(subtotal_cost_price_company),
              SUM(subtotal_company)
        FROM account_invoice_line AS line
        INNER JOIN account_invoice AS inv ON (inv.id = line.invoice_id)
        WHERE %s inv.state IN ('open', 'paid')
          AND type NOT IN ('in_invoice', 'in_refund')
          AND product_id IN %%(product_ids)s
          AND inv.company_id = %%(company_id)s
        GROUP BY product_id, type
        HAVING SUM(subtotal_cost_price_company) != 0
          AND SUM(subtotal_company) != 0
        '''
        substs = context.copy()
        substs.update(
            product_ids=tuple(res),
            company_id=company_id
            )
        date_clause = []
        if 'from_date' in substs:
            date_clause.append('inv.date_invoice >= %(from_date)s AND')
        if 'to_date' in substs:
            date_clause.append('inv.date_invoice <= %(to_date)s AND')
        query %= ' '.join(date_clause)
        cr.execute(query, substs)
        for product_id, inv_type, cost, sale in cr.fetchall():
            res[product_id]['margin_absolute'] += (sale - cost)
            tot_sale[product_id] += sale
        for product_id in tot_sale:
            if tot_sale[product_id] == 0:
                _logger.debug("Sale price for product ID %d is 0, cannot compute margin rate...", product_id)
                res[product_id]['margin_relative'] = 999.
            else:
                res[product_id]['margin_relative'] = (res[product_id]['margin_absolute'] / tot_sale[product_id]) * 100
        return res

    _columns = {
        'margin_absolute': fields.function(_compute_margin, method=True,
                                        readonly=True, type='float',
                                        string='Real Margin',
                                        multi='product_historical_margin',
                                        digits_compute=dp.get_precision('Sale Price'),
                                        help="The Real Margin [ sale price - cost price ] of the product in absolute value "
                                        "based on historical values computed from open and paid invoices."),
        'margin_relative': fields.function(_compute_margin, method=True,
                                        readonly=True, type='float',
                                        string='Real Margin (%)',
                                        multi='product_historical_margin',
                                        digits_compute=dp.get_precision('Sale Price'),
                                        help="The Real Margin [ Real Margin / sale price ] of the product in relative value "
                                        "based on historical values computed from open and paid invoices."
                                        "If no real margin set, will display 999.0 (if not invoiced yet for example)."),
        }
