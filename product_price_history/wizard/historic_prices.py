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
from openerp.osv import orm, fields
from openerp.tools.translate import _
import time


class historic_prices(orm.TransientModel):
    _name = 'historic.prices'
    _description = 'Product historical prices'

    _columns = {
        'to_date': fields.date(
            'Date',
            help='Date at which the analysis need to be done. '
            'Note that the date is understood as this day at midnight, so you may want to '
            'specify the day after ! No date is the last value.'),
        }

    def action_open_window(self, cr, uid, ids, context=None):
        """
        Open the historical prices view
        """
        if context is None:
            context = {}
        user_obj = self.pool.get('res.users')
        wiz = self.read(cr, uid, ids, [], context=context)[0]
        ctx = context.copy()
        if wiz.get('to_date'):
            ctx.update(
                to_date=wiz.get('to_date')
                )
        data_pool = self.pool.get('ir.model.data')
        filter_ids = data_pool.get_object_reference(cr, uid, 'product',
                                                    'product_search_form_view')
        product_view_id = data_pool.get_object_reference(cr, uid,
                                                         'product_price_history',
                                                         'view_product_price_history')
        if filter_ids:
            filter_id = filter_ids[1]
        else:
            filter_id = 0
        return {
            'type': 'ir.actions.act_window',
            'name': _('Historical Prices'),
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'view_id': product_view_id[1],
            'search_view_id': filter_id,
            }
