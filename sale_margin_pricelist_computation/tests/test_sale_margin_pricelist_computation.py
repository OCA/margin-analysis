from odoo.fields import Command

from odoo.addons.sale_margin.tests.test_sale_margin import TestSaleMargin


class TestSaleMarginPricelistComputation(TestSaleMargin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.write({"list_price": 20.0, "standard_price": 10.0})
        cls.margin_pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Margin Pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "name": "Test Margin",
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "margin_sale_price_formula": "result=line.price_unit",
                        }
                    ),
                ],
            }
        )

    def _create_order(self, qty=10):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.margin_pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "price_unit": 30.0,
                            "product_uom_qty": qty,
                            "product_id": self.product.id,
                        }
                    ),
                ],
            }
        )
        return order

    def test_pricelist_margin_with_formulas(self):
        order = self._create_order()
        self.assertEqual(order.margin, 200.00)
        self.assertAlmostEqual(order.margin_percent, 0.66, delta=0.01)
        pricelist_rule = self.margin_pricelist.item_ids[0]
        pricelist_rule.margin_cost_price_formula = (
            "result=product.list_price/4 if "
            "line.product_uom_qty < 15 else product.list_price/6"
        )
        order = self._create_order()
        self.assertEqual(order.margin, 250.00)
        self.assertAlmostEqual(order.margin_percent, 0.83, delta=0.01)
        order = self._create_order(20)
        self.assertAlmostEqual(order.margin, 533.4, delta=0.1)
        self.assertAlmostEqual(order.margin_percent, 0.89, delta=0.1)
