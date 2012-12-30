# -*- coding: utf-8 -*-
from openerp.osv.orm import Model
from openerp.osv import fields
import decimal_precision as dp
from tools.translate import _
import logging

class product_product(Model):
    _inherit = 'product.product'

    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        logger = logging.getLogger('product.get_cost_field')
        logger.debug("get cost field _cost_price %s, %s, %s", field_name, arg, context)
        res = {}
        for product in self.browse(cr, uid, ids):
            res[product.id] = product.standard_price + product.fix_cost_price
        return res

    _columns = {
        'fix_cost_price': fields.float(
            'Fix Cost Price', digits_compute = dp.get_precision('Sale Price')),
        'cost_price': fields.function(_cost_price,
                                      method=True,
                                      string='Cost Price',
                                      digits_compute = dp.get_precision('Sale Price'),
                                      help=_("The cost price is the standard price unless you install the product_cost_incl_bom module."))
        }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
