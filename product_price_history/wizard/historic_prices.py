# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Joel Grand-Guillaume
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
from openerp.tools.translate import _
import time
from openerp.tools import mute_logger


class historic_prices(orm.TransientModel):
    """ Will display an inventory valuation of the stock with quantity > 0
        at the given date.
    """
    _name = 'historic.prices'
    _description = 'Inventory Valuation'

    def _default_location(self, cr, uid, ids, context=None):
        try:
            ir_model = self.pool.get('ir.model.data')
            location = ir_model.get_object(cr,
                                           uid,
                                           'stock',
                                           'stock_location_stock')
            with mute_logger('openerp.osv.orm'):
                location.check_access_rule('read', context=context)
            location_id = location.id
        except (ValueError, orm.except_orm), e:
            return False
        return location_id or False

    _columns = {
        'location_id': fields.many2one(
            'stock.location',
            'Location',
            required=True,
            help='The location where you want the valuation (this will '
                 'include all the child locations.'),
        'to_date': fields.datetime(
            'Date',
            help='Date at which the analysis need to be done.'),
    }
    _defaults = {
        'location_id': _default_location,
    }

    def _get_product_qty(self, cr, uid, context=None):
        """Return all product ids that have a qty at the given location for
        the given date in the context. Use SQL for performance here.
        """
        if context is None:
            context = {}
        location_id = context.get('location')
        location_obj = self.pool.get('stock.location')
        child_location_ids = location_obj.search(cr, uid,
                                                 [('location_id',
                                                   'child_of',
                                                   [location_id])
                                                  ])
        location_ids = child_location_ids or [location_id]
        stop_date = context.get('to_date', time.strftime('%Y-%m-%d %H:%M:%S'))
        sql_req = """
                    SELECT pp.id,
                           SUM(qty) AS qty
                      FROM (SELECT p.id AS product_id,
                                   t.id AS template_id,
                                   s_in.qty
                              FROM (SELECT SUM(product_qty) AS qty,
                                           product_id
                                      FROM stock_move
                                     WHERE location_id NOT IN %(location_ids)s
                                       AND location_dest_id IN %(location_ids)s
                                       AND state = 'done'
                                       AND date <= %(stop_date)s
                                     GROUP BY product_id) AS s_in
                             INNER JOIN product_product p
                                ON p.id = s_in.product_id
                             INNER JOIN product_template t
                                ON t.id = p.product_tmpl_id
                             UNION
                            SELECT p.id AS product_id,
                                   t.id AS template_id,
                                   -s_out.qty AS qty
                              FROM (SELECT SUM(product_qty) AS qty,
                                           product_id
                                      FROM stock_move
                                     WHERE location_id IN %(location_ids)s
                                       AND location_dest_id NOT IN %(location_ids)s
                                       AND state = 'done'
                                       AND date <= %(stop_date)s
                                     GROUP BY product_id) AS s_out
                             INNER JOIN product_product p
                                ON p.id = s_out.product_id
                             INNER JOIN product_template t
                                ON t.id = p.product_tmpl_id) AS in_out
                     INNER JOIN product_template pt
                        ON pt.id = in_out.template_id
                     INNER JOIN product_product pp
                        ON pp.id = in_out.product_id
                     WHERE pt.type = 'product'
                       AND pp.active = true
                     GROUP BY pp.id
                    HAVING SUM(qty) <> 0"""
        cr.execute(sql_req,
                   {'location_ids': tuple(location_ids),
                    'stop_date': stop_date,
                    })
        res = dict(cr.fetchall())
        return res.keys()

    def action_open_window(self, cr, uid, ids, context=None):
        """
        Open the historical prices view
        """
        if context is None:
            context = {}
        wiz = self.read(cr, uid, ids, [], context=context)[0]
        ctx = context.copy()
        ctx.update(
            location=wiz.get('location_id')[0],
        )
        if wiz.get('to_date'):
            ctx.update(
                to_date=wiz.get('to_date')
                )
        displayed_ids = self._get_product_qty(cr, uid, context=ctx)
        domain = [('id', 'in', displayed_ids)]
        d_obj = self.pool.get('ir.model.data')
        filter_ids = d_obj.get_object_reference(cr, uid, 'product',
                                                'product_search_form_view')
        product_view_id = d_obj.get_object_reference(cr, uid,
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
            'domain': domain,
            'search_view_id': filter_id,
            }

