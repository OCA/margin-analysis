# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestSaleMarginSync(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Pricelist for testing sale_margin_sync"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "test_product",
                "type": "consu",
                "is_storable": True,
                "standard_price": 70,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 30.0,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100.00,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.env.ref("uom.product_uom_dozen").id,
                            "price_unit": 1200.00,
                        },
                    ),
                ],
                "pricelist_id": cls.pricelist.id,
            }
        )

    def test_sale_margin_sync(self):
        self.order.action_confirm()
        so_line1 = self.order.order_line[:1]
        move1 = so_line1.move_ids[:1]
        move1.write({"quantity": 10, "picked": True})
        so_line2 = self.order.order_line[1:2]
        move2 = so_line2.move_ids[:1]
        move2.write({"quantity": 2, "picked": True})
        self.order.picking_ids[:1]._action_done()
        move1.stock_valuation_layer_ids[:1].unit_cost = 80.0
        move2.stock_valuation_layer_ids[:1].unit_cost = 80.0
        self.assertEqual(so_line1.purchase_price, 80.0)
        self.assertEqual(so_line1.margin, 200.0)
        self.assertEqual(so_line2.purchase_price, 960.0)
        self.assertEqual(so_line2.margin, 480)

    def test_sale_margin_sync_unvalidated_move(self):
        self.order.action_confirm()
        so_line1 = self.order.order_line[:1]
        move1 = so_line1.move_ids[:1]
        move1.write({"quantity": 10, "picked": True})
        move1.stock_valuation_layer_ids[:1].unit_cost = 80.0
        so_line2 = self.order.order_line[1:2]
        move2 = so_line2.move_ids[:1]
        move2.write({"quantity": 2, "picked": True})
        move2.stock_valuation_layer_ids[:1].unit_cost = 80.0
        self.assertEqual(so_line1.purchase_price, 70.0)
        self.assertEqual(so_line1.margin, 300.0)
        self.assertEqual(so_line2.purchase_price, 840.0)
        self.assertEqual(so_line2.margin, 720)
