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
    ##     """override in subclass if you need to setup a custom way of computing the standard price"""
    ##     " XXX fonction statique qui renvoie le prix standard en fonction d'une liste d'id de product"
    ##     return self.standard_price # XXX or a string?


    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        print "get cost field _cost_price", field_name, arg, context
        res = {}
        for product in self.browse(cr, uid, ids):
            res[product.id] = product.standard_price
        return res

    _columns = {
        'cost_price': fields.function(_cost_price,
                                      method=True,
                                      string='Cost Price',
                                      digits_compute = dp.get_precision('Sale Price'),
                                      help="The cost is the standard price")
        }
