# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ChangeProductCost(models.TransientModel):
    _name = 'change.product.cost'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    standard_price = fields.Float(
        string='Cost',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost of the product template used for standard stock valuation "
             "in accounting and used as a base price on purchase orders. "
             "Expressed in the default unit of measure of the product.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        required=True,
        default=lambda s: s._default_currency_id(),
    )

    @api.model
    def _default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    @api.multi
    def confirm_cost(self):
        self.ensure_one()
        company = self.env.user.company_id
        cost = self.standard_price
        cost = self.currency_id.compute(cost, company.currency_id)
        self.product_id.standard_price = cost

    @api.model
    def _get_cost(self, product):
        return product.standard_price

    @api.model
    def default_get(self, fields_list):
        values = super(ChangeProductCost, self).default_get(fields_list)
        product_id = values.get('product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            values['standard_price'] = self._get_cost(product)
        return values

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.standard_price = self._get_cost(self.product_id)
