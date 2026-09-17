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
        """Check purchase_price in sale report"""
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

    def test_sale_report_margin_other_currency(self):
        """The cost of an order in another currency is reported in the company one.

        Scenario:
            1. Set up a currency worth half of the company currency.
            2. Confirm an order in that currency with one line sold at 10 with
               a cost of 8.
        Expected:
            - The report row shows a unit price of 5 and a purchase price of 4,
              both in the company currency.
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
