# Copyright (C) 2012 - Today: Camptocamp SA
# Copyright (C) 2016 - Today: GRAP (http://www.grap.coop)
# @author: Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, api
from odoo.models import Model

import odoo.addons.decimal_precision as dp


class ProductProduct(Model):
    _inherit = 'product.product'

    @api.depends('product_tmpl_id.standard_price', 'standard_price')
    def _compute_replenishment_cost(self):
        for product in self:
            product.replenishment_cost = product.standard_price

    replenishment_cost = fields.Float(
        string='Replenishment cost', compute='_compute_replenishment_cost',
        store=True, digits=dp.get_precision('Product Price'),
        help="The cost that you have to support in order to produce or "
             "acquire the goods. Depending on the modules installed, "
             "this cost may be computed based on various pieces of "
             "information, for example Bills of Materials or latest "
             "Purchases. By default, the Replenishment cost is the same "
             "as the Cost Price.")
