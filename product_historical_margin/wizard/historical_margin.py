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
import time
import logging

from openerp.osv.orm import TransientModel
from openerp.osv import fields
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
class historical_margin(TransientModel):
    _name = 'historical.margin'
    _description = 'Product historical margin'

    def _get_product_ids(self, cr, uid, context=None):
        if context is None: context = {}
        res = False
        if (context.get('active_model', False) == 'product.product' and
                context.get('active_ids', False)):
            res = context['active_ids']
        return res


    _columns = {
        'from_date': fields.date('From', help='Date of the first invoice to take into account. '
                                 'The earliest existing invoice will be used if left empty'),
        'to_date': fields.date('To', help='Date of the last invoice to take into account. '
                               'The latest existing invoice will be used if left empty'),
        'product_ids': fields.many2many('product.product', string='Products'),
        }
    _defaults = {
        'from_date': time.strftime('%Y-01-01'),
        'to_date': time.strftime('%Y-12-31'),
        'product_ids': _get_product_ids,
        }

    def action_open_window(self, cr, uid, ids, context=None):
        """
        Open the historical margin view
        """

        if context is None:
            context = {}
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        wiz = self.read(cr, uid, ids, [], context=context)[0]
        ctx = context.copy()
        ctx.update(
            from_date=wiz.get('from_date'),
            to_date=wiz.get('to_date')
            )
        product_ids = wiz.get('product_ids')
        data_pool = self.pool.get('ir.model.data')
        filter_ids = data_pool.get_object_reference(cr, uid, 'product',
                                                    'product_search_form_view')
        product_view_id = data_pool.get_object_reference(cr, uid,
                                                         'product_historical_margin',
                                                         'view_product_historical_margin')
        if filter_ids:
            filter_id = filter_ids[1]
        else:
            filter_id = 0
        if not product_ids:
            _logger.info('no ids supplied. Computing ids of sold products')
            query = '''SELECT DISTINCT product_id
                    FROM account_invoice_line AS line
                    INNER JOIN account_invoice AS inv ON (inv.id = line.invoice_id)
                    WHERE %s inv.state IN ('open', 'paid')
                      AND type NOT IN ('in_invoice', 'in_refund')
                      AND inv.company_id = %%(company_id)s
                    '''
            date_clause = []
            if 'from_date' in ctx:
                date_clause.append('inv.date_invoice >= %(from_date)s AND')
            if 'to_date' in ctx:
                date_clause.append('inv.date_invoice <= %(to_date)s AND')
            query %= ' '.join(date_clause)
            ctx['company_id'] = company_id
            cr.execute(query, ctx)
            product_ids = [row[0] for row in cr.fetchall()]
        domain = [('id','in',product_ids)]
        _logger.info('domains = %s', domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Historical Margins'),
            'context': ctx,
            'domain': domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'view_id': product_view_id[1],
            'search_view_id': filter_id,
            }
