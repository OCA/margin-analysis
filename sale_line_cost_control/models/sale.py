# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, tools


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    purchase_price_missing = fields.Boolean(
        compute='_compute_purchase_price_missing',
        string='Missing Cost',
    )

    @api.depends('purchase_price')
    def _compute_purchase_price_missing(self):
        precision_model = self.env['decimal.precision']
        precision = precision_model.precision_get('Product Price')
        for line in self:
            line.purchase_price_missing = tools.float_is_zero(
                line.purchase_price,
                precision_digits=precision
            )
