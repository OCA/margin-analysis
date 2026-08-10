from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon


@tagged("post_install", "-at_install")
class TestRewardMarginComputation(TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Main Product",
                "list_price": 35.0,
                "standard_price": 11.52,
            }
        )

        cls.reward_product_1 = cls.env["product.product"].create(
            {
                "name": "Reward Product 1",
                "list_price": 11.0,
                "standard_price": 11.0,
            }
        )

        cls.reward_product_2 = cls.env["product.product"].create(
            {
                "name": "Reward Product 2",
                "list_price": 14.0,
                "standard_price": 14.0,
            }
        )

        cls.program = cls.env["loyalty.program"].create(
            {
                "name": "Test Program",
                "program_type": "promotion",
                "trigger": "auto",
                "applies_on": "current",
                "rule_ids": [
                    Command.create(
                        {
                            "minimum_qty": 2,
                            "product_ids": [Command.set(cls.main_product.ids)],
                        }
                    )
                ],
                "reward_ids": [
                    Command.create(
                        {
                            "reward_type": "multi_gift",
                            "reward_product_id": cls.reward_product_1.id,
                            "loyalty_multi_gift_ids": [
                                Command.create(
                                    {
                                        "reward_default_product_id": (
                                            cls.reward_product_1.id
                                        ),
                                        "reward_product_quantity": 1,
                                        "reward_product_ids": [
                                            Command.set(cls.reward_product_1.ids)
                                        ],
                                    }
                                ),
                                Command.create(
                                    {
                                        "reward_default_product_id": (
                                            cls.reward_product_2.id
                                        ),
                                        "reward_product_quantity": 2,
                                        "reward_product_ids": [
                                            Command.set(cls.reward_product_2.ids)
                                        ],
                                    }
                                ),
                                Command.create(
                                    {
                                        "reward_default_product_id": (
                                            cls.main_product.id
                                        ),
                                        "reward_product_quantity": 1,
                                        "reward_product_ids": [
                                            Command.set(cls.main_product.ids)
                                        ],
                                    }
                                ),
                            ],
                            "sale_margin_formula": (
                                """
reward_lines_cost = 0
for reward_line in reward_lines:
    reward_lines_cost += reward_line.purchase_price * reward_line.product_uom_qty
result=origin_line.margin - reward_lines_cost + 19
                            """
                            ),
                        }
                    )
                ],
            }
        )

    def _create_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.main_product.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 35.0,
                        }
                    )
                ],
            }
        )

    def test_reward_applies_and_margin_is_computed(self):
        order = self._create_order()
        main_line = order.order_line.filtered(
            lambda line: line.product_id == self.main_product and not line.reward_id
        )
        order.action_open_reward_wizard()
        reward_lines = order.order_line.filtered(lambda line: line.reward_id)
        self.assertTrue(main_line, "Main line not found")
        self.assertTrue(reward_lines, "Reward lines not found")
        self.assertEqual(len(reward_lines), 3)
        for reward_line in reward_lines:
            self.assertIn(main_line, reward_line.reward_origin_generated_line_ids)
        # 46.96 - 11.52 - 11.0 - 2*14 + 19
        calculated_margin = 15.44
        distributed_lines = main_line | reward_lines
        self.assertAlmostEqual(
            sum(distributed_lines.mapped("margin")), calculated_margin, delta=0.1
        )
        self.assertAlmostEqual(main_line.margin, 3.7)
        self.assertAlmostEqual(main_line.margin_percent, 0.05)
        self.assertAlmostEqual(
            sum(distributed_lines.mapped("margin_percent")),
            calculated_margin / main_line.price_subtotal,
            delta=0.1,
        )
        self.assertTrue(all(reward_lines.mapped("margin_percent")))
        self.assertAlmostEqual(order.margin, calculated_margin, delta=0.1)

    def test_formula(self):
        with self.assertRaises(ValidationError):
            self.program.reward_ids[0].sale_margin_formula = "test=3+ '"
