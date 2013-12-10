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

from __future__ import division

import logging
from itertools import chain
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class Product(orm.Model):
    _inherit = 'product.product'

    def _compute_purchase_price(self, cr, uid, ids, context=None):
        '''
        Compute the purchase price, taking into account sub products and routing
        '''
        if context is None:
            context = {}
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties', [])

        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')

        res = {}
        ids = ids or []
        print "_compute_purchase_price with ids %s" % ids

        product_without_bom_ids = []
        for pr in self.browse(cr, uid, ids, context=context):
            bom_id = bom_obj._bom_find(cr, uid, pr.id, product_uom=product_uom,
                                       properties=bom_properties)
            if not bom_id:  # no BoM: use standard_price
                product_without_bom_ids.append(pr.id)
                continue
            _logger.debug("look for product named %s, bom_id is %s", pr.name, bom_id)
            bom = bom_obj.browse(cr, uid, bom_id)
            sub_products, routes = bom_obj._bom_explode(cr, uid, bom,
                                                        factor=1,
                                                        properties=bom_properties,
                                                        addthis=True)
            price = 0.
            for sub_product_dict in sub_products:
                sub_product = self.browse(cr, uid,
                                          sub_product_dict['product_id'],
                                          context=context)
                std_price = sub_product.cost_price
                # std_price = sub_product.standard_price
                qty = uom_obj._compute_qty(
                    cr, uid,
                    from_uom_id=sub_product_dict['product_uom'],
                    qty=sub_product_dict['product_qty'],
                    to_uom_id=sub_product.uom_po_id.id)
                price += std_price * qty
            if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    hour = ((wc.time_start + wc.time_stop + cycle * wc.time_cycle)
                            * (wc.time_efficiency or 1.0))
                    price += wc.costs_cycle * cycle + wc.costs_hour * hour
            price /= bom.product_qty
            price = uom_obj._compute_price(
                cr, uid, bom.product_uom.id,
                price, bom.product_id.uom_id.id)
            res[pr.id] = price
        if product_without_bom_ids:
            standard_prices = super(Product, self)._compute_purchase_price(
                cr, uid, product_without_bom_ids, context=context)
            print "cost_price for products without boms gives %s" % standard_prices
            res.update(standard_prices)
        return res

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        return self._compute_purchase_price(cr, uid, ids, context=context)

    def _get_bom_product(self, cr, uid, ids, context=None):
        """ return ids of modified product and ids of all product that use
        as sub-product one of this ids.

        Example::

            BoM:
                Product A
                    - Product B
                    - Product C

        => If we change standard_price of product B, we want to update
        Product A as well...

        """
        def _get_parent_bom(bom_record):
            """ Recursively find the parent bom of all the impacted products
            and return a list of bom ids

            """
            bom_result = []
            if bom_record.bom_id:
                bom_result.append(bom_record.bom_id.id)
                bom_result.extend(_get_parent_bom(bom_record.bom_id))
            return bom_result

         # def _get_product_bom_existing(product_record):
         #    """
         #    faire pareil mais regarder pour les produits si a une autre parent bom si 
         #    pas sortir de la boucle. appeler _get_parent_bom pour savoir ça
         #    """
         #    product_result=[]
         #    bom_obj = self.pool.get('mrp.bom')
         #    bom_ids = bom_obj.search(cr, uid, [('product_id','=',product.id)], 
         #                        context=context)
         #    for bom in bom_obj.browse(cr, uid, bom_ids, context=context):
         #        res = _get_parent_bom(bom)
         #    return True

        res = []
        product_ids = []
        bom_obj = self.pool.get('mrp.bom')
        bom_ids = bom_obj.search(cr, uid, [('product_id', 'in', ids)],
                                 context=context)
        if not bom_ids:
            return ids

        boms = bom_obj.browse(cr, uid, bom_ids, context=context)
        parent_bom_ids = set(chain.from_iterable(_get_parent_bom(bom) for
                                                 bom in boms))
        bom_ids = set(bom_ids)
        bom_ids.update(parent_bom_ids)
        product_ids = set(product_ids)
        bom_product_ids = self._get_product_id_from_bom(cr, uid, list(bom_ids),
                                                        context=context)
        product_ids.update(bom_product_ids)

#         final_bom_ids = bom_ids
#         for bom in bom_obj.browse(cr, uid, bom_ids, context=context):
#             res = _get_parent_bom(bom)
#         final_bom_ids = list(set(res + bom_ids))
#         product_from_bom_ids = self._get_product_id_from_bom(
#             cr, uid, final_bom_ids, context=context)
#         product_ids = list(set(ids + product_from_bom_ids))

        # result = self._get_bom_product(cr, uid, product_ids, context=context)
        # product_ids.extend(result)
        # #manque condition de sortie
        return list(product_ids)

    def _get_product(self, cr, uid, ids, context=None):
        """ Return all product impacted from a change in a bom, that means
        current product and all parent that is composed by it.

        """
        bom_obj = self.pool.get('mrp.bom')
        prod_obj = self.pool.get('product.product')
        res = set()
        for bom in bom_obj.browse(cr, uid, ids, context=context):
            res.add(bom.product_id.id)
        final_res = prod_obj._get_bom_product(cr, uid, list(res),
                                              context=context)
        return final_res

    def _get_product_id_from_bom(self, cr, uid, ids, context=None):
        """ Return a list of product ids from bom """
        bom_obj = self.pool.get('mrp.bom')
        res = set()
        for bom in bom_obj.browse(cr, uid, ids, context=context):
            res.add(bom.product_id.id)
        return list(res)

    def _get_product_from_template2(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        res = prod_obj._get_product_from_template(cr, uid, ids, context=context)
        return res

    # Trigger on product.product is set to None, otherwise do not trigg
    # on product creation !
    _cost_price_triggers = {
        'product.product': (_get_bom_product, None, 10),
        # 'product.product': (_get_bom_product, ['standard_price','bom_ids'], 20),
        'product.template': (_get_product_from_template2,
                             ['standard_price'], 10),
        'mrp.bom': (_get_product,
                    ['bom_id',
                     'bom_lines',
                     'product_id',
                     'product_uom',
                     'product_qty',
                     'product_uos',
                     'product_uos_qty',
                     ],
                    10)
    }

    _columns = {
        'cost_price': fields.function(
            _cost_price,
            store=_cost_price_triggers,
            string='Cost Price (incl. BoM)',
            digits_compute=dp.get_precision('Sale Price'),
            help="The cost price is the standard price or, if the "
                 "product has a bom, the sum of all standard price "
                 "of its components. it take also care of the bom "
                 "costing like cost per cycle.")
    }
