#  Copyright 2019 Tecnativa - Sergio Teruel
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo.tests import Form, TransactionCase


class TestSaleMarginDelivered(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.product_uom_id = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "product",
                "uom_id": cls.product_uom_id.id,
                "standard_price": 10.0,
                "list_price": 20.00,
                "tracking": "none",
            }
        )
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "partner test", "property_product_pricelist": cls.pricelist.id}
        )
        cls.quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.src_location.id,
                "quantity": 100.0,
            }
        )

    def _new_sale_order(self):
        sale_order_form = Form(self.SaleOrder)
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product
            order_line_form.product_uom_qty = 6
        return sale_order_form.save()

    def get_return_picking_wizard(self, picking):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return stock_return_picking_form.save()

    def test_sale_margin_ordered(self):
        sale_order = self._new_sale_order()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 0.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.0)
        self.assertEqual(order_line.purchase_price_delivery, 0.0)

    def test_sale_margin_delivered(self):
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.qty_done = 3.0
        picking._action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 30.0)
        self.assertEqual(order_line.margin_delivered_percent, 50.0)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_zero(self):
        sale_order = self._new_sale_order()
        order_line = sale_order.order_line[:1]
        order_line.product_uom_qty = 0.0
        self.assertEqual(order_line.margin_delivered, 0.0)
        self.assertEqual(order_line.margin_delivered_percent, 0)

    def _create_return(self, picking, to_refund=False):
        return_wiz = self.get_return_picking_wizard(picking)
        return_wiz.product_return_moves.write({"quantity": 3.0, "to_refund": to_refund})
        new_picking_id, pick_type_id = return_wiz._create_returns()
        return self.env["stock.picking"].browse(new_picking_id)

    def _validate_so_picking(self, sale_order):
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.qty_done = 6.0
        picking._action_done()
        return picking

    def test_sale_margin_delivered_return_to_refund(self):
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = self._validate_so_picking(sale_order)
        picking_return = self._create_return(picking, to_refund=True)
        picking_return.move_line_ids.qty_done = 3.0
        picking_return._action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 30.0)
        self.assertEqual(order_line.margin_delivered_percent, 50.0)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered_return_no_refund(self):
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = self._validate_so_picking(sale_order)
        picking_return = self._create_return(picking, to_refund=False)
        picking_return.move_line_ids.qty_done = 3.0
        picking_return._action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 60.0)
        self.assertEqual(order_line.margin_delivered_percent, 50.0)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)
