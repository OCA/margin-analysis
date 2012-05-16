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

    ## def get_cost_field(self):
    ##     """overriden from product_get_cost_field"""
    ##     return self.standard_price # XXX or a string?



    def _compute_purchase_price(self, cursor, user, ids,
                                pricelist=None,
                                product_uom=None,
                                bom_properties=None):
        '''
        Compute the purchase price

        As it explodes the sub product on 1 level

        This is not implemented for BoM having sub BoM producing more than 1
        product qty.
        Rewrite _compute_purchase_price and remove mrp constraint to fix this.
        '''
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
            res[pr.id] = 0.0
            for sub_product_dict in sub_products:
                sub_product = self.browse(cursor, user, sub_product_dict['product_id'])
                std_price = sub_product.standard_price
                qty = uom_obj._compute_qty(cursor, user,
                                           from_uom_id = sub_product_dict['product_uom'],
                                           qty         = sub_product_dict['product_qty'],
                                           to_uom_id   = sub_product.uom_po_id.id)
                res[pr.id] += std_price * qty
                # TODO alf use routes to compute cost of manufacturing (following is from product_extended)
                ## if bom.routing_id:
                ##     for wline in bom.routing_id.workcenter_lines:
                ##         wc = wline.workcenter_id
                ##         cycle = wline.cycle_nbr
                ##         hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) *  (wc.time_efficiency or 1.0)
                ##         price += wc.costs_cycle * cycle + wc.costs_hour * hour
                ##         price = self.pool.get('product.uom')._compute_price(cr,uid,bom.product_uom.id,price,bom.product_id.uom_id.id)
        return res


    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        pricelist = context.get('pricelist')
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties')
        res = self._compute_purchase_price(cr, uid, ids, pricelist, product_uom, bom_properties)
        return res

    _columns = {
        'cost_price': fields.function(_cost_price,
                                      methode=True,
                                      string='Cost Price (incl. BoM)',
                                      digits_compute = dp.get_precision('Sale Price'),
                                      help="The cost is the standard price")
        }
