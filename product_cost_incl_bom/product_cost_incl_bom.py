# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
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

from openerp.osv.orm import Model
from openerp.osv import fields
import decimal_precision as dp

class Product(Model):
    _inherit = 'product.product'

    def _compute_purchase_price(self, cursor, user, ids,
                                product_uom=None,
                                bom_properties=None,
                                context=None):
        '''
        Compute the purchase price, taking into account sub products and routing
        '''
        if context is None:
            context = {}
        if bom_properties is None:
            bom_properties =  []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')

        res = {}
        ids = ids or []

        for pr in self.browse(cursor, user, ids):

            # Workaround for first loading in V5 as some columns are not created
            #if not hasattr(pr, 'standard_price'): return False
            bom_id = bom_obj._bom_find(cursor, user, pr.id, product_uom=None, properties=bom_properties)
            if not bom_id: # no BoM: use standard_price
                res[pr.id] = pr.standard_price
                continue
            bom = bom_obj.browse(cursor, user, bom_id)
            sub_products, routes = bom_obj._bom_explode(cursor, user, bom,
                                                        factor=1,
                                                        properties=bom_properties,
                                                        addthis=True)
            price = 0.
            for sub_product_dict in sub_products:
                sub_product = self.browse(cursor, user, sub_product_dict['product_id'])
                std_price = sub_product.standard_price
                qty = uom_obj._compute_qty(cursor, user,
                                           from_uom_id = sub_product_dict['product_uom'],
                                           qty         = sub_product_dict['product_qty'],
                                           to_uom_id   = sub_product.uom_po_id.id)
                price += std_price * qty
            if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) *  (wc.time_efficiency or 1.0)
                    price += wc.costs_cycle * cycle + wc.costs_hour * hour
            price /= bom.product_qty
            price = uom_obj._compute_price(cursor, user, bom.product_uom.id, price, bom.product_id.uom_id.id)
            res[pr.id] = price
        return res

    def get_cost_field(self, cr, uid, ids, context=None):
        return self._cost_price(cr, uid, ids, '', [], context)

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties')
        res = self._compute_purchase_price(cr, uid, ids, product_uom, bom_properties)
        return res

    _columns = {
        'cost_price': fields.function(_cost_price,
                                      method=True,
                                      string='Cost Price (incl. BoM)',
                                      digits_compute = dp.get_precision('Sale Price'),
                                      help="The cost price is the standard price or, if the product has a bom, "
                                      "the sum of all standard price of its components. it take also care of the "
                                      "bom costing like cost per cylce.")
        }
