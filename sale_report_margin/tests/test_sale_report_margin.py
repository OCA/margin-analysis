# Copyright 2023 Álvaro Marcos <alvaro.marcos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.orm.commands import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleReportMargin(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_product = cls.env["product.product"].create(
            {"name": "Product Test"}
        )

    def test_sale_report_margin(self):
        """Check the purchase price and margin of a line in the sale report.

        Scenario:
            1. Confirm an order with one line sold at 10 with a cost of 8.
        Expected:
            - The report row shows a purchase price of 8.
            - The report row shows a margin of 2, that is 20% of the untaxed total.
        """
        order = self.env["sale.order"].create(
            {
                "name": "Test Order",
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_product.id,
                            "price_unit": 10.0,
                            "product_uom_qty": 1.0,
                            "purchase_price": 8.0,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        report = self.env["sale.report"].search(
            [
                ("order_reference", "=", f"{order._name},{order.id}"),
                ("product_id", "=", self.product_product.id),
            ]
        )
        self.assertEqual(report.purchase_price, 8.0)
        self.assertEqual(report.margin, 2.0)
        self.assertEqual(report.margin_percent, 0.2)

    def test_sale_report_margin_percent_no_subtotal(self):
        """A free line has no margin percentage instead of a division error.

        Scenario:
            1. Confirm an order with one line sold at 0 with a cost of 8.
        Expected:
            - The report row shows a margin of -8 and a margin percentage of 0.
        """
        order = self.env["sale.order"].create(
            {
                "name": "Test Order",
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_product.id,
                            "price_unit": 0.0,
                            "product_uom_qty": 1.0,
                            "purchase_price": 8.0,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        report = self.env["sale.report"].search(
            [("order_reference", "=", f"{order._name},{order.id}")]
        )
        self.assertEqual(report.margin, -8.0)
        self.assertEqual(report.margin_percent, 0.0)

    def test_sale_report_margin_other_currency(self):
        """Amounts of an order in another currency are reported in the company one.

        Scenario:
            1. Set up a currency worth half of the company currency.
            2. Confirm an order in that currency with one line sold at 10 with
               a cost of 8.
        Expected:
            - The report row shows a unit price of 5, a purchase price of 4 and
              a margin of 1, all in the company currency.
            - The margin percentage is still 20%.
        """
        currency = self.quick_ref("base.EUR")
        currency.active = True
        self.env["res.currency.rate"].create(
            {
                "currency_id": currency.id,
                "company_id": self.env.company.id,
                "name": fields.Date.today(),
                "rate": 2.0,
            }
        )
        pricelist = self.env["product.pricelist"].create(
            {"name": "Test Pricelist", "currency_id": currency.id}
        )
        order = self.env["sale.order"].create(
            {
                "name": "Test Order",
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_product.id,
                            "price_unit": 10.0,
                            "product_uom_qty": 1.0,
                            "purchase_price": 8.0,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        report = self.env["sale.report"].search(
            [("order_reference", "=", f"{order._name},{order.id}")]
        )
        self.assertEqual(report.price_unit, 5.0)
        self.assertEqual(report.purchase_price, 4.0)
        self.assertEqual(report.margin, 1.0)
        self.assertEqual(report.margin_percent, 0.2)
