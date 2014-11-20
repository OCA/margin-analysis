# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Numérigraphe SARL.
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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


_logger = logging.getLogger(__name__)


# This is defined as a function, not a method, because we're going to inject
# it directly via ProductProduct.__init__(), and that's how
# fields.function.__init__() sees it usually
def _get_product_from_po_line(self, cr, uid, ids, context=None):
    """Find the products to update when Purchase Order Lines change"""
    # Use read_group to get the distinct product ids
    products_groups = self.pool['purchase.order.line'].read_group(
        cr, uid, [('id', 'in', ids)], ['product_id'], ['product_id'],
        context=context)
    product_ids = [g['product_id'][0] for g in products_groups]
    # Let's also update the products which depend on this one
    res = self.pool['product.product']._get_product_from_product(
        cr, uid, product_ids, context=context)
    return res


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    # Initialization (no context)
    def __init__(self, pool, cr):
        """Add a new trigger to update the cost based on Purchase Order Lines

        Doing it in __init__ is more modular than copying and pasting the field
        definition in _columns.
        """
        # TODO: new API in v8 probably let us do it in a simpler way
        s = super(ProductProduct, self)
        s._cost_price_triggers['purchase.order.line'] = (
            _get_product_from_po_line, ['product_id',
                                         'product_uom',
                                         'price_unit',
                                         'state',
                                         'date_planned',
                                        ], 10)
        s.__init__(pool, cr)

    def _compute_purchase_price(self, cr, uid, ids, context=None):
        """Use the latest purchase price."""
        _logger.debug("_compute_purchase_price with ids %s" % ids)
        res = super(ProductProduct, self)._compute_purchase_price(
            cr, uid, ids, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        line_obj = self.pool['purchase.order.line']
        uom_obj = self.pool['product.uom']
        # It would have been nice to be able to use read_group here
        # Unfortunately it seems to be able to MAX() values only if the field
        # is defined to do so.
        for product_id in ids:
            # Find the latest purchase order line
            latest_po_ids = line_obj.search(
                cr, uid, [('product_id', '=', product_id),
                          ('state', '!=', 'cancel')],
                order='date_planned DESC', limit=1, context=context)
            if latest_po_ids:
                # Get the line's price, converted to the default UoM
                line = line_obj.browse(
                    cr, uid, latest_po_ids[0], context=context)
                res[product_id] = uom_obj. _compute_price(
                    cr, uid, line.product_uom.id,
                    line.price_unit, line.product_id.uom_id.id)
        _logger.debug('Latest purchase prices: %s' % res)
        return res
