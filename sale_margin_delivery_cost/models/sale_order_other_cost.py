# Copyright (C) 2021 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrderOtherCost(models.Model):
    _name = "sale.order.other.cost"
    _description = "Sales Order Other Cost"

    order_id = fields.Many2one(
        "sale.order",
        string="Sales Order",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )
    name = fields.Text(string="Description", required=True)
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain="[('type', '!=', 'product'), "
        "'|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True,
        ondelete="restrict",
        check_company=True,
    )
    price_unit = fields.Float("Cost", digits="Product Price")
    company_id = fields.Many2one(
        related="order_id.company_id", store=True, readonly=True, index=True
    )
    is_delivery = fields.Boolean(string="Is a Delivery", default=False)
    recompute_delivery_price = fields.Boolean(
        related="order_id.recompute_delivery_price"
    )

    @api.onchange("product_id")
    def product_id_change(self):
        if self.product_id:
            self.name = self.product_id.display_name
