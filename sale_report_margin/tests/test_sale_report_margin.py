# Copyright 2023 Álvaro Marcos <alvaro.marcos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleReportMargin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_product = cls.env["product.product"].create(
            {"name": "Product Test"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner Test"})

    def test_sale_report_margin(self):
        """Check purchase_price in sale report"""
        order = self.env["sale.order"].create(
            {
                "name": "Test Order",
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
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
