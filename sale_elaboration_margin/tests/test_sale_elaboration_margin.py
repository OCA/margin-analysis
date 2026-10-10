# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleElaborationMargin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100.0}
        )
        cls.product_elaboration_a = cls.env["product.product"].create(
            {
                "name": "Product Elaboration A",
                "type": "service",
                "list_price": 50.0,
                "standard_price": 20.0,
                "is_elaboration": True,
                "taxes_id": False,
            }
        )
        cls.product_elaboration_b = cls.env["product.product"].create(
            {
                "name": "Product Elaboration B",
                "type": "service",
                "list_price": 25.0,
                "standard_price": 10.0,
                "is_elaboration": True,
                "taxes_id": False,
            }
        )
        cls.elaboration_a = cls.env["product.elaboration"].create(
            {
                "code": "AA",
                "name": "Elaboration A",
                "product_id": cls.product_elaboration_a.id,
            }
        )
        cls.elaboration_b = cls.env["product.elaboration"].create(
            {
                "code": "BB",
                "name": "Elaboration B",
                "product_id": cls.product_elaboration_b.id,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test pricelist"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )

    def _create_sale_order(self, elaborations):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 10
            for elaboration in elaborations:
                line_form.elaboration_ids.add(elaboration)
        return order_form.save()

    def _get_pending_temporary_lines(self):
        """Lines never saved that are still waiting for a recomputation."""
        lines = self.env["sale.order.line"]
        for field in self.env.fields_to_compute():
            if field.model_name == lines._name:
                lines |= self.env.records_to_compute(field)
        return lines.filtered(lambda line: not line.id)

    def test_elaboration_price(self):
        order = self._create_sale_order(self.elaboration_a)
        line = order.order_line
        self.assertEqual(line.elaboration_price, 50.0)
        self.assertEqual(line.elaboration_cost_price, 20.0)
        self.assertEqual(line.elaboration_margin, 300.0)
        line.elaboration_ids = self.elaboration_a + self.elaboration_b
        self.assertEqual(line.elaboration_price, 75.0)
        self.assertEqual(line.elaboration_cost_price, 30.0)
        line.elaboration_ids = False
        self.assertEqual(line.elaboration_price, 0.0)
        self.assertEqual(line.elaboration_cost_price, 0.0)

    def test_elaboration_price_temporary_line_not_pending(self):
        """The line used to get the elaboration price is not recomputed later.

        That line has no order, so it has neither company nor currency. If it
        stays waiting for a recomputation, it's computed together with the real
        lines the next time one of those fields is read, breaking any compute
        method that needs the currency of the line.
        """
        order = self._create_sale_order(self.elaboration_a)
        line = order.order_line
        line.elaboration_ids = self.elaboration_b
        self.assertEqual(line.elaboration_price, 25.0)
        self.assertFalse(self._get_pending_temporary_lines())
