# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase
from odoo.tests import Form


class TestSaleMarginMrp(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Pricelist for testing sale_margin_mrp',
        })
        cls.product_kit = cls.env["product.product"].create({
            "name": "Product test 1",
            "type": "consu",
        })
        cls.product_kit_comp_1 = cls.env["product.product"].create({
            "name": "Product Component 1",
            "type": "product",
            "standard_price": "70",
        })
        cls.product_kit_comp_2 = cls.env["product.product"].create({
            "name": "Product Component 2",
            "type": "product",
            "standard_price": "33",
        })
        cls.bom = cls.env["mrp.bom"].create({
            "product_id": cls.product_kit.id,
            "product_tmpl_id": cls.product_kit.product_tmpl_id.id,
            "type": "phantom",
            "bom_line_ids": [
                (0, 0, {
                    "product_id": cls.product_kit_comp_1.id,
                    "product_qty": 2,
                }),
                (0, 0, {
                    "product_id": cls.product_kit_comp_2.id,
                    "product_qty": 4,
                })
            ]})
        cls.product_2 = cls.env["product.product"].create({
            "name": "Product test 2",
            "type": "product",
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Partner test",
            "property_product_pricelist": cls.pricelist.id,
        })

    def test_sale_margin_mrp(self):
        self.assertAlmostEqual(0, self.product_kit.standard_price)
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_kit
        sale_order = order_form.save()
        self.assertAlmostEqual(272, sale_order.order_line.purchase_price)
        self.assertAlmostEqual(272, self.product_kit.standard_price)
