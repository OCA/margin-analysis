# -*- coding: utf-8 -*-
# © 2012 Alexandre Fayolle,Yannick Vaucher,Joël Grand-Guillaume,Camptocamp
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
import logging
from itertools import chain

from openerp import models, api

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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_purchase_price(self):
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
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        computed = {}
        if not self._ids:
            return {}
        _logger.debug("_compute_purchase_price with ids %s" % list(self._ids))

        depends = dict((product.id, set()) for product in self)
        product_bom = {}
        for product in self:
            bom_id = bom_obj._bom_find(
                product_tmpl_id=product.product_tmpl_id.id,
                product_id=product.id)
            if not bom_id:  # no BoM: use standard_price
                computed[product.id] = product.standard_price
                continue
            bom = bom_obj.browse(bom_id)
            if bom.type == 'phantom' and not bom.bom_line_ids:
                # work around lp:1281054 calling _bom_explode in that
                bom_id = False
                computed[product.id] = product.standard_price
                continue
            # case will cause an infinite recursion
            subproducts, routes = bom_obj._bom_explode(
                bom, product, factor=1)
            # set the dependencies of "product_id"
            depends[product.id].update([sp['product_id']
                                        for sp in subproducts])
            product_bom[product.id] = {
                'bom': bom,
                'subproducts': subproducts
            }

        # eagerly read all the dependencies products
        read_ids = list(chain.from_iterable(depends.itervalues()))
        sub_read = self.browse(read_ids).read(
            ['replenishment_cost', 'uom_po_id'])
        subproduct_costs = dict((p['id'], p) for p in sub_read)

        ordered = list(chain.from_iterable(topological_sort(depends)))

        # extract all the products not in a bom and get their costs
        # first, avoid to read them one by one
        no_bom_ids = [
            p_id for p_id in ordered
            if p_id not in product_bom and p_id in self._ids]
        if (set(no_bom_ids) == set(self._ids)) and not bom_id:
            return computed
        if no_bom_ids:
            costs = self.browse(no_bom_ids)._compute_purchase_price()
            computed.update(costs)

        for product_id in ordered:
            if product_id not in self._ids:
                # the product is a dependency so it appears in the
                # topological sort, but the cost price should not be
                # recomputed
                continue
            if product_id not in product_bom:
                # already computed with ``super``
                continue

            cost = 0.0
            subproduct_infos = product_bom[product_id]['subproducts']
            for subproduct_info in subproduct_infos:
                subproduct_id = subproduct_info['product_id']
                subproduct = subproduct_costs[subproduct_id]
                # The cost price could have been recomputed in an
                # earlier iteration.  Thanks to the topological sort,
                # the subproducts are always computed before their
                # parents
                subcost = computed.get(subproduct_id, subproduct[
                                       'replenishment_cost'])
                qty = uom_obj._compute_qty(
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
                bom.product_uom.id, cost, bom.product_id.uom_id.id)
            computed[product_id] = cost

        return computed

    @api.multi
    def _compute_replenishment_cost(self):
        super(ProductProduct, self)._compute_replenishment_cost()
        res = self._compute_purchase_price()
        for product in self:
            product.replenishment_cost = res.get(product.id, 0)
