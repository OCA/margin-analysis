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

class account_invoice(Model):
    _inherit = 'account.invoice'

    def _refund_cleanup_lines(self, cr, uid, lines, context=None):
        for line in lines:
            line.invoice_user_id = False
        return super(account_invoice, self)._refund_cleanup_lines(cr, uid, 
          lines, context=context)


class account_invoice_line(Model):
    """
    The goal on the invoice line model is only to store the minimum needed values to
    allow analysis and computation of margin at product level.
    Later, we'll be able to provide as well a view based on an invoice line SQL view,
    so user will be allowed to play with filter and group by.
    """
    _inherit = 'account.invoice.line'

    def _compute_line_values(self, cr, uid, ids, field_names, arg, context=None):
        """
        Compute cost_price, cost_price in company currency and subtotal in company currency
        that will be used for margin analysis. This method is called by the function fields.

        Those values will be stored, so we'll be able to use them in analysis.

        WARNING !! All subtotal in company currency will be with the right sign. For example,
        if I have a customer refund, the sign will be - For all infos in invoice currency, we
        kept the standard logic => always positif.

        :return dict of dict of the form :
            {INT Line ID : {
                    float subtotal_cost_price_company,
                    float subtotal_cost_price,
                    float subtotal_company
                    float margin_absolute
                    }}
        """
        res = {}
        if not ids:
            return res
        
        if context is None:
            context = {}
        ctx = context.copy()
        user_obj = self.pool.get('res.users')
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        company_obj = self.pool.get('res.company')
       
        fields = [
                'subtotal_cost_price_company',
                'subtotal_cost_price',
                'subtotal_company',
                'margin_absolute',
                'margin_relative'
                ]
        for line_id in ids:
            res[line_id] = dict.fromkeys(fields, 0.0)
        for obj in self.browse(cr, uid, ids, context=context):
            # The company must be the one of the invoice in case a ir.cron create the invoice
            # with admin user. We need to pass it in the context as well
            # if we use also product_price_history with this module
            if obj.company_id:
                company = obj.company_id
            else:
                company_id = company_obj._company_default_get(
                                                              cr,
                                                              uid,
                                                              'account.invoice',
                                                              context=context)
                company = company_obj.browse(cr, uid, company_id, context=context)
            company_currency_id = company.currency_id.id
            ctx['company_id'] = company.id
            if not obj.product_id:
                continue
            product = product_obj.read(cr, uid, obj.product_id.id,
                                       ['id','cost_price'], context=ctx)
            if obj.invoice_id.currency_id is None:
                currency_id = company_currency_id
            else:
                currency_id = obj.invoice_id.currency_id.id
            if obj.invoice_type in ('out_refund','in_invoice'):
                factor = -1.
            else:
                factor = 1.

            subtotal_cost_price_company = factor * product['cost_price'] * obj.quantity
            # Convert price_subtotal from invoice currency to company currency
            subtotal_company = factor * currency_obj.compute(cr, uid, currency_id,
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
            margin_absolute = subtotal_company - subtotal_cost_price_company
            if subtotal_company == 0:
                margin_relative = 999.
            else:
                margin_relative = (margin_absolute / subtotal_company) * 100
            res[obj.id] = {
                'subtotal_cost_price_company': subtotal_cost_price_company,
                'subtotal_cost_price': subtotal_cost_price,
                'subtotal_company': subtotal_company,
                'margin_absolute': margin_absolute,
                'margin_relative': margin_relative,
                }
            _logger.debug("The following values has been computed for product ID %d: subtotal_cost_price=%f"
                "subtotal_cost_price_company=%f, subtotal_company=%f", product['id'], subtotal_cost_price,
                subtotal_cost_price_company, subtotal_company)
        return res

    def _recalc_margin(self, cr, uid, ids, context=None):
        return ids

    def _recalc_margin_parent(self, cr, uid, ids, context=None):
        res=[]
        for inv in self.browse(cr, uid, ids, context=context):
            for line in inv.invoice_line:
                res.append(line.id)
        return res

    _col_store = {'account.invoice.line': (_recalc_margin,
                                           ['price_unit', 'product_id', 'discount','invoice_line_tax_id'],
                                           20),
                  'account.invoice':  (_recalc_margin_parent,
                                       ['currency_id'],
                                       20),
                  }

    _columns = {
        'subtotal_cost_price_company': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Cost',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The cost subtotal of the line at the time of the creation of the invoice, "
                                              "express in the company currency."),
        'subtotal_cost_price': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Cost in currency',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The cost subtotal of the line at the time of the creation of the invoice, "
                                              "express in the invoice currency."),
        'subtotal_company': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Net Sales',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The subtotal (VAT excluded) of the line at the time of the creation of the invoice, "
                                              "express in the company currency (computed with the rate at invoice creation time, as we "
                                              "don't have the cost price of the product at the date of the invoice)."),
        'margin_absolute': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Real Margin',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              group_operator="sum",
                                              help="The Real Margin [ net sale - cost ] of the line."),
        'margin_relative': fields.function(_compute_line_values, method=True, readonly=True,type='float',
                                              string='Real Margin (%)',
                                              multi='product_historical_margin',
                                              store=_col_store,
                                              digits_compute=dp.get_precision('Account'),
                                              help="The Real Margin % [ (Real Margin / net sale) * 100 ] of the line."
                                              "If no real margin set, will display 999.0 (if not invoiced yet for example)."),

        # Those field are here to better report to the user from where the margin is computed
        # this will allow him to understand why a margin is of that amount using the link
        # from product to invoice lines
        'invoice_state': fields.related('invoice_id', 'state', type='selection',
                                                selection=[
                                                    ('draft','Draft'),
                                                    ('proforma','Pro-forma'),
                                                    ('proforma2','Pro-forma'),
                                                    ('open','Open'),
                                                    ('paid','Paid'),
                                                    ('cancel','Cancelled')
                                                    ],
                                                readonly=True, string="Invoice state",
                                                help='The parent invoice state'),
        'invoice_type': fields.related('invoice_id', 'type', type='selection', store=True,
                                                selection=[
                                                    ('out_invoice','Customer Invoice'),
                                                    ('in_invoice','Supplier Invoice'),
                                                    ('out_refund','Customer Refund'),
                                                    ('in_refund','Supplier Refund'),
                                                    ],
                                                readonly=True, string="Invoice type",
                                                help='The parent invoice type'),
        'invoice_user_id': fields.related('invoice_id','user_id',type='many2one',relation='res.users',string='Salesman', store=True),
        'invoice_date': fields.related('invoice_id','date_invoice',type='date',string='Invoice Date'),

        }

    def read_group(self, cr, uid, domain, fields, groupby, 
            offset=0, limit=None, context=None, orderby=False):
        """The percentage of the relative margin has to be recomputed asit is nor 
        a sum, nor a avg, but a percentage of 2 valuesof the line computed as:
        margin_relative = margin_absolute / subtotal_company * 100"""
        if not context:
            context = {}
        if groupby:
            res = super(account_invoice_line, self).read_group(cr, uid,
                domain, fields, groupby,
                offset=offset, limit=limit, context=context, orderby=orderby)
            for re in res:
                margin_relative = 0.0
                if re.get('margin_relative', False):
                    # percentage of margin = (margin_absolute / subtotal_company) * 100
                    margin_absolute = re.get('margin_absolute', 0)
                    subtotal_company = re.get('subtotal_company', 0)
                    if subtotal_company == 0.0:
                        margin_relative = 999
                    else:
                        margin_relative = margin_absolute / subtotal_company * 100
                    re['margin_relative'] = margin_relative
                else:
                    if re.get('__context', False):
                        margin_absolute = re['__context'].get('margin_absolute', 0)
                        subtotal_company = re.get('subtotal_company', 0)
                        if subtotal_company == 0.0:
                            margin_relative = 999
                        else:
                            margin_relative = margin_absolute / subtotal_company * 100
                if re.get('__context', False):
                    re['__context']['margin_relative'] = margin_relative
        return res
