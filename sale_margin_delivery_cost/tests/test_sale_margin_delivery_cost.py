# Copyright (C) 2021 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleMarginDeliveryCost(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "list_price": 100.0,
                "standard_price": 60.0,
            }
        )
        cls.carrier_product = cls.env["product.product"].create(
            {
                "name": "Carrier Product",
                "type": "service",
                "list_price": 15.0,
            }
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test Carrier",
                "product_id": cls.carrier_product.id,
                "delivery_type": "fixed",
                "charge_policy": "other",
            }
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom_id": self.uom_unit.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_margin_with_other_cost(self):
        order = self._create_sale_order()
        order._compute_margin()
        self.assertEqual(order.margin, 40.0)
        self.env["sale.order.other.cost"].create(
            {
                "order_id": order.id,
                "name": "Packaging",
                "price_unit": 10.0,
            }
        )
        order._compute_margin()
        self.assertEqual(order.margin, 30.0)
        self.assertEqual(order.margin_percent, 0.3)

    def test_margin_with_other_cost_without_sales_amount(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.env["sale.order.other.cost"].create(
            {
                "order_id": order.id,
                "name": "Packaging",
                "price_unit": 10.0,
            }
        )

        order._compute_margin()

        self.assertEqual(order.margin, -10.0)
        self.assertFalse(order.margin_percent)

    def test_set_delivery_line_other_policy(self):
        order = self._create_sale_order()
        order.set_delivery_line(self.carrier, 15.0)
        self.assertEqual(order.carrier_id, self.carrier)
        self.assertFalse(order.order_line.filtered("is_delivery"))
        self.assertEqual(len(order.other_cost_ids), 1)
        self.assertEqual(order.other_cost_ids.price_unit, 15.0)
        self.assertEqual(order.other_cost_ids.product_id, self.carrier_product)
        order._compute_margin()
        self.assertEqual(order.margin, 25.0)

    def test_set_delivery_line_other_policy_with_product_description(self):
        self.carrier_product.description_sale = "Delivery description"
        order = self._create_sale_order()

        order.set_delivery_line(self.carrier, 15.0)

        self.assertEqual(
            order.other_cost_ids.name,
            "Test Carrier: Delivery description",
        )

    def test_other_cost_product_onchange(self):
        other_cost = self.env["sale.order.other.cost"].new()

        other_cost.product_id_change()
        self.assertFalse(other_cost.name)

        other_cost.product_id = self.product
        other_cost.product_id_change()

        self.assertEqual(other_cost.name, self.product.display_name)

    def test_set_delivery_line_sale_policy(self):
        order = self._create_sale_order()
        carrier = self.carrier.copy({"charge_policy": "sale"})
        order.set_delivery_line(carrier, 15.0)
        delivery_lines = order.order_line.filtered("is_delivery")
        self.assertEqual(len(delivery_lines), 1)
        self.assertEqual(delivery_lines.price_unit, 15.0)
        self.assertFalse(order.other_cost_ids)
