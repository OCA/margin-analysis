# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2012 Camptocamp SA
#    Copyright 2012 Endian Solutions BV
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

class product_product(Model):
    _inherit = 'product.product'

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        product_uom = context.get('product_uom')
        bom_properties = context.get('properties')
        res = self._compute_purchase_price(cr, uid, ids, product_uom,
                                           bom_properties, context=context)
        for self_obj in self.browse(cr, uid, ids, context=context):
            res[self_obj.id] = res[self_obj.id] + self_obj.fixed_cost_price
        return res

    _columns = {
        'fixed_cost_price': fields.float(
            'Fixed Cost Price', digits_compute = dp.get_precision('Sale Price')),
        'cost_price': fields.function(_cost_price,
                                      string='Cost Price (incl. BoM)',
                                      digits_compute=dp.get_precision('Sale Price'),
                                      help="The cost price is the standard price or, if the product has a BoM, "
                                      "the sum of all standard prices of its components. It also takes care of the "
                                      "BoM costing like cost per cylce.")
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
