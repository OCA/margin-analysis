from odoo.tests.common import TransactionCase


class TestSaleElaborationMargin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company

        # Setup Pricelist
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "currency_id": cls.company.currency_id.id,
            }
        )

        # Setup Partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )

        # Setup Product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )

        # Setup Elaboration Product
        cls.elaboration_product = cls.env["product.product"].create(
            {
                "name": "Test Elaboration",
                "type": "service",
                "list_price": 20.0,
                "standard_price": 15.0,
            }
        )

        # Add taxes to the elaboration product to cover tax compute block
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Test Tax 10%",
                "amount_type": "percent",
                "amount": 10.0,
                "price_include_override": "tax_included",
            }
        )
        cls.elaboration_product.taxes_id = [(6, 0, cls.tax.ids)]

        # Setup Sale Order
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
            }
        )

        # Setup Sale Order Line
        cls.sale_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "product_uom_qty": 2.0,
                "price_unit": 100.0,
            }
        )

    def test_sale_elaboration_margin(self):
        # Initial check with no elaboration
        self.sale_line._compute_elaboration_price()
        self.assertEqual(self.sale_line.elaboration_price, 0.0)
        self.assertEqual(self.sale_line.elaboration_cost_price, 0.0)

        elaboration = self.env["product.elaboration"].create(
            {
                "name": "Test Elaboration Profile",
                "product_id": self.elaboration_product.id,
            }
        )
        self.sale_line.write({"elaboration_ids": [(4, elaboration.id)]})

        self.sale_line._compute_elaboration_price()

        # Elaboration price should be the price of the elaboration
        # product from the pricelist, minus included taxes.

        self.assertTrue(self.sale_line.elaboration_price > 0.0)

        # Elaboration cost price should be standard_price * 1
        # (because the compute loop adds it directly per elaboration product)

        self.assertEqual(self.sale_line.elaboration_cost_price, 15.0)

        # Test margin computation
        self.sale_line._compute_elaboration_margin()

        # Qty is 2.0
        expected_margin = 2.0 * (
            self.sale_line.elaboration_price - self.sale_line.elaboration_cost_price
        )
        self.assertAlmostEqual(self.sale_line.elaboration_margin, expected_margin)
