# Copyright (C) 2021 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    other_cost_ids = fields.One2many(
        "sale.order.other.cost",
        "order_id",
        string="Other Costs",
        states={"cancel": [("readonly", True)], "done": [("readonly", True)]},
        copy=True,
        auto_join=True,
    )

    @api.depends("order_line.margin", "amount_untaxed", "other_cost_ids.price_unit")
    def _compute_margin(self):
        super()._compute_margin()
        # Subtract other costs from the Sales Order margin
        for order in self.filtered("other_cost_ids"):
            other_costs = sum(order.mapped("other_cost_ids.price_unit"))
            order.margin -= other_costs
            order.margin_percent = (
                order.amount_untaxed and order.margin / order.amount_untaxed
            )

    def set_delivery_line(self, carrier, amount):
        # Using the UPDATE SHIPPING COST button sets an Other Costs line with the cost,
        # instead of a Sales Order line.
        # This is because we are not charging this cost to the customer.
        # We use it to have a better Sales Order margin calculation.

        # For "sale" charging policy, use standard logic - shipping as an SO line.
        # For "other" charging policy, set the delivery cost in the Other Costs field.
        if carrier.charge_policy == "sale":
            super(SaleOrder, self).set_delivery_line(carrier, amount)
        else:
            for order in self:
                order.carrier_id = carrier.id
                carrier_with_partner_lang = carrier.with_context(
                    lang=self.partner_id.lang
                )
                if carrier_with_partner_lang.product_id.description_sale:
                    so_description = "%s: %s" % (
                        carrier_with_partner_lang.name,
                        carrier_with_partner_lang.product_id.description_sale,
                    )
                else:
                    so_description = carrier_with_partner_lang.name
                values = {
                    "order_id": self.id,
                    "name": so_description,
                    "product_id": carrier.product_id.id,
                    "is_delivery": True,
                    "price_unit": amount,
                }
                order.other_cost_ids.filtered("is_delivery").unlink()
                order.other_cost_ids.create(values)
        return True
