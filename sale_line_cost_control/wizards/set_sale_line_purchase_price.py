# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SetSaleLinePurchasePrice(models.TransientModel):
    _name = 'set.sale.line.purchase.price'

    line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Line',
        readonly=True,
        required=True,
        default=lambda s: s._default_line_id()
    )
    purchase_price = fields.Float(
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
        default=lambda s: s._default_currency_id()
    )

    def _default_line_id(self):
        assert self.env.context['active_model'] == 'sale.order.line'
        line_id = self.env.context.get('active_id')
        return line_id

    def _default_currency_id(self):
        company = self.env.user.company_id
        return company.currency_id.id

    @api.multi
    def confirm_purchase_price(self):
        self.ensure_one()
        company = self.env.user.company_id
        currency_at_date = self.currency_id.with_context(
            date=self.line_id.order_id.date_order
        )
        cost = currency_at_date.compute(self.purchase_price,
                                        company.currency_id)
        self.line_id.purchase_price = cost
