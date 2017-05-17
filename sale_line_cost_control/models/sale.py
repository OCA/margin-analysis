# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, exceptions, fields, models, tools


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cost_missing = fields.Boolean(
        compute='_compute_product_standard_price',
        string='Missing Cost',
    )
    product_standard_price = fields.Float(
        compute='_compute_product_standard_price',
        string='Cost',
        groups="base.group_user",
    )

    @api.depends('product_id.standard_price')
    def _compute_product_standard_price(self):
        precision_model = self.env['decimal.precision']
        precision = precision_model.precision_get('Product Price')
        for line in self:
            if not line.product_id:
                line.cost_missing = True
                continue
            line.cost_missing = tools.float_is_zero(
                line.product_id.standard_price,
                precision_digits=precision
            )
            line.product_standard_price = line.product_id.standard_price

    @api.multi
    def action_add_cost_on_product(self):
        self.ensure_one()
        if not self.product_id:
            raise exceptions.UserError(
                _('The line has no product, cannot set a cost price.')
            )
        action_xmlid = ('sale_line_cost_control.'
                        'action_change_product_cost')
        action = self.env.ref(action_xmlid).read()[0]
        action['context'] = {
            'product_readonly': True,
            'default_product_id': self.product_id.id,
            'default_currency_id': self.order_id.currency_id.id,
        }
        return action
