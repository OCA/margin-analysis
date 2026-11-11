# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.orm.commands import Command
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestSaleReportMarginSecurity(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_cost = new_test_user(
            cls.env,
            login="sale_manager_cost",
            groups="sales_team.group_sale_manager,product_cost_security.group_product_cost",
        )
        cls.product = cls.env["product.product"].create({"name": "Product Test"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "price_unit": 10.0,
                            "product_uom_qty": 1.0,
                            "purchase_price": 8.0,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()
        cls.domain = [
            ("order_reference", "=", f"{cls.order._name},{cls.order.id}"),
            ("product_id", "=", cls.product.id),
        ]

    def test_cost_user_reads_margin_data(self):
        """A user allowed to see the cost reads the margin data of the report."""
        report = self.env["sale.report"].with_user(self.user_cost).search(self.domain)
        self.assertEqual(report.purchase_price, 8.0)
        self.assertEqual(report.margin_percent, 0.2)
