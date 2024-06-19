#  Copyright 2024 Moduon Team
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl


from odoo.addons.sale_margin_delivered.tests.test_sale_margin_delivered import (
    TestSaleMarginDelivered,
)


class TestSaleMarginDeliveredDropship(TestSaleMarginDelivered):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create(
            {"name": "supplier test", "property_product_pricelist": cls.pricelist.id}
        )
        dropship_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        cls.dropship_product = cls.env["product.product"].create(
            {
                "name": "Dropship Product Test",
                "type": "product",
                "uom_id": cls.product_uom_id.id,
                "standard_price": 10.0,
                "list_price": 20.00,
                "tracking": "none",
                "route_ids": [(6, 0, dropship_route.ids)],
            }
        )
        cls.dropship_product.seller_ids = [
            (0, 0, {"partner_id": cls.supplier.id, "price": 3.0})
        ]

    def test_sale_margin_delivered_dropship(self):
        """Delivered quantities by Dropship"""
        sale_order = self._new_sale_order(product=self.dropship_product)
        sale_order.action_confirm()
        purchases = sale_order._get_purchase_orders()
        purchases.button_confirm()
        dropship_picking = purchases.picking_ids
        dropship_picking.move_line_ids.qty_done = 6.0
        dropship_picking._action_done()
        # Create return for Dropship
        picking_return = self._create_return(
            dropship_picking, qty_refund=3.0, to_refund=True
        )
        picking_return.action_assign()
        picking_return.move_line_ids.qty_done = 3.0
        picking_return._action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 30.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)
