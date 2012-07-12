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

from openerp.osv.orm import TransientModel
from openerp.osv import fields
from openerp.tools.translate import _


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
        wiz = self.read(cr, uid, ids, [], context)[0]
        ctx = context.copy()
        ctx['from_date']  = wiz.get('from_date')
        ctx['to_date'] = wiz.get('to_date')
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
        if product_ids:
            domain = [('id','in',product_ids)]
        else:
            domain = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Historical Margins'),
            'context': ctx,
            'domain':domain,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'view_id': product_view_id[1],
            'search_view_id': filter_id,
            }
