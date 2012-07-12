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

class account_invoice_line(Model):
    """
    The goal on the invoice line model is only to store the minimum needed values to
    allow analysis and computation of margin at product level.
    Later, we'll be able to provide as well a view based on an invoice line SQL view,
    so user will be allowed to play with filter and group by.
    """
    _inherit = 'account.invoice.line'

    def _compute_line_values(self, cr, uid, ids, field_names,  arg, context=None):
        """
        Compute cost_price, cost_price in company currency and subtotal in company currency
        that will be used for margin analysis. This method is called by the function fields.
        
        Those values will be stored, so we'll be able to use them in analysis.
        
        :return dict of dict of the form : 
            {INT Line ID : {
                    float subtotal_cost_price_company,
                    float subtotal_cost_price,
                    float subtotal_company
                    }}
        """
        if context is None:
            context = {}
        res = {}
        if not ids:
            return res
        logger = logging.getLogger('product_historical_margin')
        user_obj = self.pool.get('res.users')
        company_currency_id = user_obj.browse(cr, uid, uid).company_id.currency_id.id
        currency_obj = self.pool.get('res.currency')
        for line_id in ids:
            res[line_id] = {
                    'subtotal_cost_price_company': 0.0,
                    'subtotal_cost_price': 0.0,
                    'subtotal_company': 0.0
                    }
        for obj in self.browse(cr, uid, ids):
            product = obj.product_id
            subtotal_cost_price_company = product.cost_price * obj.quantity
            if obj.invoice_id.currency_id is None:
                currency_id = company_currency_id
            else:
                currency_id = obj.invoice_id.currency_id.id
            # Convert price_subtotal from invoice currency to company currency
            subtotal_company = currency_obj.compute(cr, uid, currency_id,
                                                                  company_currency_id,
                                                                  obj.price_subtotal,
                                                                  round=False,
                                                                  context=context)
            # Compute the subtotal_cost_price values from company currency in invoice currency
            subtotal_cost_price = currency_obj.compute(cr, uid, company_currency_id,
                                                                  currency_id,
                                                                  subtotal_cost_price_company,
                                                                  round=False,
                                                                  context=context)
            res[obj.id] = {
                'subtotal_cost_price_company': subtotal_cost_price_company,
                'subtotal_cost_price': subtotal_cost_price,
                'subtotal_company': subtotal_company,
            }
            logger.debug("The following values has been computed for product ID %d: subtotal_cost_price=%f"
                "subtotal_cost_price_company=%f, subtotal_company=%f", product.id, subtotal_cost_price, 
                subtotal_cost_price_company, subtotal_company)
        return res

    def _recalc_margin(self, cr, uid, ids, context=None):
        return ids

    def _recalc_margin_parent(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res=[]
        for inv in self.browse(cr,uid,ids):
            for line in inv.invoice_line:
                res.append(line.id)
        return res

    _col_store = {'account.invoice.line': (_recalc_margin,
                                           ['price_unit', 'product_id', 'discount'],
                                           20),
                  'account.invoice':  (_recalc_margin_parent,
                                       ['currency_id'],
                                       20),
                  }

    _columns = {
        'subtotal_cost_price_company': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Total Cost (company currency)',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The cost subtotal of the line at the time of the creation of the invoice, "
                                              "express in the company currency."),
        'subtotal_cost_price': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Total Cost',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The cost subtotal of the line at the time of the creation of the invoice, "
                                              "express in the invoice currency."),
        'subtotal_company': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Total Without Tax (company currency)',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The subtotal (VAT excluded) of the line at the time of the creation of the invoice, " 
                                              "express in the company currency (computed with the rate at invoice creation time, as we "
                                              "don't have the cost price of the product at the date of the invoice)."),
        'invoice_type': fields.related('invoice_id', 'type', type='selection', store=True,
                                        selection=[
                                            ('out_invoice','Customer Invoice'),
                                            ('in_invoice','Supplier Invoice'),
                                            ('out_refund','Customer Refund'),
                                            ('in_refund','Supplier Refund'),
                                            ],
                                        readonly=True, string="Invoice type",
                                        help='optimize queries when computing the margins'),
        }
