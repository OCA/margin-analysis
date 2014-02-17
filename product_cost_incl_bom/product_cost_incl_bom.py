# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle, Guewen Baconnier, Joel Grand-Guillaume
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


def topological_sort(data):
    """ Topological sort on a dict expressing dependencies.

    Recipe from:
    http://code.activestate.com/recipes/578272-topological-sort/
    Slightly modified, adapted for Python 2.6

    Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependences, each subsequent set consists of items that depend upon
    items in the preceeding sets.

    >>> print '\\n'.join(repr(sorted(x)) for x in topological_sort({
    ...     2: set([11]),
    ...     9: set([11,8]),
    ...     10: set([11,3]),
    ...     11: set([7,5]),
    ...     8: set([7,3]),
    ...     }) )
    [3, 5, 7]
    [8, 11]
    [2, 9, 10]

    """
    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = set.union(*data.itervalues()) - set(data.iterkeys())
    # Add empty dependences where needed
    data.update(dict((item, set()) for item in extra_items_in_deps))
    while True:
        ordered = set(item for item, dep in data.iteritems() if not dep)
        if not ordered:
            break
        yield ordered
        data = dict((item, (dep - ordered))
                    for item, dep in data.iteritems()
                    if item not in ordered)
    assert not data, \
        "Cyclic dependencies exist among these items " \
        ":\n%s" % '\n'.join(repr(x) for x in data.iteritems())


class product_product(orm.Model):
    _inherit = 'product.product'

    def _compute_purchase_price(self, cr, uid, ids, context=None):
        """ Compute the purchase price of products

        Take into account the sub products (bills of materials) and the
        routing.

        As an example, we have such a hierarchy of products::

            - Table A
                - 2x Plank 20.-
                - 4x Wood leg 10.-
            - Table B
                - 3x Plank 20.-
                - 4x Red wood leg
            - Red wood leg
                - 1x Wood leg 10.-
                - 1x Red paint pot 10.-
            - Chair
                - 1x Plank
                - 4x Wood leg
            - Table and Chair
                - 1x Table Z
                - 4x Chair Z

        When we update the ``standard_price`` of a "Wood leg", all cost
        prices of the products upper in the tree must be computed again.
        Here, that is: "Table A", "Red wood leg", "Chair", "Table B".
        The price of all theses products are computed at the same
        time in this function, the effect is that we should take:

        1. to not read the cost price of a product in the browse_record,
           if it is computed here because it has likely changed, but use
           the new cost instead
        2. compute the prices in a topological order, so we start at the
           leaves of the tree thus we know the prices of all the sub
           products when we go up the tree

        The topological sort, in this example, when we modify the "Wood
        leg", will returns successively 3 generators::

            [set('Wood plank', 'Red Paint Pot', 'Wood Leg')],
            [set('Table A', 'Red wood leg')],
            [set('Table B')]]

        The first set having no dependencies and the subsequent sets
        having items that depend upon items in the preceding set.

        """
        if context is None:
            context = {}
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties', [])

        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')

        computed = {}
        if not ids:
            return computed
        _logger.debug("_compute_purchase_price with ids %s" % ids)

        depends = dict((product_id, set()) for product_id in ids)
        product_bom = {}
        for product_id in ids:
            bom_id = bom_obj._bom_find(cr, uid, product_id,
                                       product_uom=product_uom,
                                       properties=bom_properties)
            if not bom_id:  # no BoM: use standard_price
                continue
            bom = bom_obj.browse(cr, uid, bom_id, context=context)
            if bom.type == 'phantom' and not bom.bom_lines:
                continue # work around lp:1281054 calling _bom_explode in that
                         # case will cause an infinite recursion
            subproducts, routes = bom_obj._bom_explode(cr, uid, bom,
                                                       factor=1,
                                                       properties=bom_properties,
                                                       addthis=True)
            # set the dependencies of "product_id"
            depends[product_id].update([sp['product_id'] for sp in
                                        subproducts])
            product_bom[product_id] = {
                'bom': bom,
                'subproducts': subproducts
            }

        # eagerly read all the dependencies products
        sub_read = self.read(cr, uid,
                             list(chain.from_iterable(depends.itervalues())),
                             ['cost_price', 'uom_po_id'], context=context)
        subproduct_costs = dict((p['id'], p) for p in sub_read)

        ordered = list(chain.from_iterable(topological_sort(depends)))

        # extract all the products not in a bom and get their costs
        # first, avoid to read them one by one
        no_bom_ids = [p_id for p_id in ordered if
                      p_id not in product_bom and
                      p_id in ids]
        costs = super(product_product, self)._compute_purchase_price(
            cr, uid, no_bom_ids, context=context)
        computed.update(costs)

        for product_id in ordered:
            if not product_id in ids:
                # the product is a dependency so it appears in the
                # topological sort, but the cost price should not be
                # recomputed
                continue
            if product_id not in product_bom:
                # already computed with ``super``
                continue

            cost = 0.
            subproduct_infos = product_bom[product_id]['subproducts']
            for subproduct_info in subproduct_infos:
                subproduct_id = subproduct_info['product_id']
                subproduct = subproduct_costs[subproduct_id]
                # The cost price could have been recomputed in an
                # earlier iteration.  Thanks to the topological sort,
                # the subproducts are always computed before their
                # parents
                subcost = computed.get(subproduct_id, subproduct['cost_price'])
                qty = uom_obj._compute_qty(
                    cr, uid,
                    from_uom_id=subproduct_info['product_uom'],
                    qty=subproduct_info['product_qty'],
                    to_uom_id=subproduct['uom_po_id'][0])
                cost += subcost * qty

            bom = product_bom[product_id]['bom']
            if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    hour = ((wc.time_start + wc.time_stop +
                             cycle * wc.time_cycle) *
                            (wc.time_efficiency or 1.0))
                    cost += wc.costs_cycle * cycle + wc.costs_hour * hour
            cost /= bom.product_qty

            cost = uom_obj._compute_price(
                cr, uid, bom.product_uom.id,
                cost, bom.product_id.uom_id.id)
            computed[product_id] = cost

        return computed

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

        bom_obj = self.pool.get('mrp.bom')
        bom_ids = bom_obj.search(cr, uid, [('product_id', 'in', ids)],
                                 context=context)
        if not bom_ids:
            return ids

        boms = bom_obj.browse(cr, uid, bom_ids, context=context)
        parent_bom_ids = set(chain.from_iterable(_get_parent_bom(bom) for
                                                 bom in boms))
        bom_ids = set(bom_ids)
        product_ids = set(ids)
        # product ids from the other BoMs
        bom_product_ids = self._get_product_id_from_bom(
            cr, uid, list(parent_bom_ids), context=context)
        product_ids.update(bom_product_ids)
        # recurse in the other BoMs to find all the product ids
        recurs_ids = self._get_bom_product(cr, uid,
                                           bom_product_ids,
                                           context=context)
        product_ids.update(recurs_ids)
        return list(product_ids)

    def _get_product(self, cr, uid, ids, context=None):
        """ Return all product impacted from a change in a bom, that means
        current product and all parent that is composed by it.

        """
        bom_obj = self.pool.get('mrp.bom')
        prod_obj = self.pool.get('product.product')
        res = set()
        for bom in bom_obj.read(cr, uid, ids, ['product_id'], context=context):
            res.add(bom['product_id'][0])
        final_res = prod_obj._get_bom_product(cr, uid,
                                              list(res),
                                              context=context)
        _logger.debug("trigger on mrp.bom model for product ids %s", final_res)
        return final_res

    def _get_product_id_from_bom(self, cr, uid, ids, context=None):
        """ Return a list of product ids from bom """
        bom_obj = self.pool.get('mrp.bom')
        res = set()
        for bom in bom_obj.read(cr, uid, ids, ['product_id'], context=context):
            res.add(bom['product_id'][0])
        return list(res)

    def _get_product_from_template2(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        res = prod_obj._get_product_from_template(cr, uid, ids, context=context)
        return res

    # Trigger on product.product is set to None, otherwise do not trigg
    # on product creation !
    _cost_price_triggers = {
        'product.product': (_get_bom_product, None, 5),
        'product.template': (_get_product_from_template2,
                             ['standard_price'], 5),
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
            digits_compute=dp.get_precision('Product Price'),
            help="The cost price is the standard price or, if the "
                 "product has a bom, the sum of all standard price "
                 "of its components. it take also care of the bom "
                 "costing like cost per cycle.")
    }
