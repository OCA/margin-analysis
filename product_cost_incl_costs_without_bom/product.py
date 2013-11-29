# -*- coding: utf-8 -*-
from openerp.osv.orm import Model
from openerp.osv import fields
import decimal_precision as dp
import logging

class product_product(Model):
    _inherit = 'product.product'

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = product.standard_price + product.fixed_cost_price
        return res

    _columns = {
        'fixed_cost_price': fields.float(
            'Fixed Cost Price', digits_compute = dp.get_precision('Sale Price')),
        'cost_price': fields.function(_cost_price,
                                      string='Cost Price',
                                      digits_compute=dp.get_precision('Sale Price'),
                                      help="The cost price is the standard price unless you install the product_cost_incl_bom module.")
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
