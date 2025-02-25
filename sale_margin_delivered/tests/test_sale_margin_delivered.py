#  Copyright 2019 Tecnativa - Sergio Teruel
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo.tests import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleMarginDelivered(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.SaleOrder = cls.env["sale.order"]
        cls.product_uom_id = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "consu",
                "uom_id": cls.product_uom_id.id,
                "standard_price": 10.0,
                "list_price": 20.00,
                "tracking": "none",
                "is_storable": True,
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

    def _new_sale_order(self, product=None, product_qty=6.0):
        """Create a new Order with desired product and quantity"""
        if not product:
            product = self.product
        sale_order_form = Form(self.SaleOrder)
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = product
            order_line_form.product_uom_qty = product_qty
        return sale_order_form.save()

    def get_return_picking_wizard(self, picking):
        """Returns the wizard to create a return picking"""
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return stock_return_picking_form.save()

    def test_sale_margin_ordered(self):
        """Non confirmed Order"""
        sale_order = self._new_sale_order()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 0.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.0)
        self.assertEqual(order_line.purchase_price_delivery, 0.0)

    def test_sale_margin_delivered(self):
        """Delivered less quantities than ordered"""
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_ids.quantity = 3.0
        picking.with_context(skip_backorder=True).button_validate()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 30.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered_excess(self):
        """Delivered quantities exceed ordered quantities"""
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.quantity = 12.0
        picking.with_context(skip_backorder=True).button_validate()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 120.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_zero(self):
        """Zero quantities Order"""
        sale_order = self._new_sale_order()
        order_line = sale_order.order_line[:1]
        order_line.product_uom_qty = 0.0
        self.assertEqual(order_line.margin_delivered, 0.0)
        self.assertEqual(order_line.margin_delivered_percent, 0)

    def _create_return(self, picking, qty_refund=3.0, to_refund=False):
        """Creates a return picking"""
        return_wiz = self.get_return_picking_wizard(picking)
        return_wiz.product_return_moves.write(
            {"quantity": qty_refund, "to_refund": to_refund}
        )
        res = return_wiz.action_create_returns()
        return self.env["stock.picking"].browse(res["res_id"])

    def _validate_so_picking(self, sale_order, qty_done=6.0):
        """Validate picking"""
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.quantity = qty_done
        picking.with_context(skip_backorder=True).button_validate()
        return picking

    def test_sale_margin_delivered_return_to_refund(self):
        """Delivered same quantities than ordered and return half on a refund"""
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = self._validate_so_picking(sale_order, qty_done=6.0)
        picking_return = self._create_return(picking, qty_refund=3.0, to_refund=True)
        picking_return.move_line_ids.quantity = 3.0
        picking_return.with_context(skip_backorder=True).button_validate()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 30.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered_return_to_refund_excess(self):
        """Delivered quantities exceed ordered quantities and return with refund"""
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = self._validate_so_picking(sale_order, qty_done=12.0)
        picking_return = self._create_return(picking, qty_refund=3.0, to_refund=True)
        picking_return.move_line_ids.quantity = 3.0
        picking_return.with_context(skip_backorder=True).button_validate()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 90.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered_return_no_refund(self):
        """Delivered same quantities than ordered and return without refund"""
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = self._validate_so_picking(sale_order, qty_done=6.0)
        picking_return = self._create_return(picking, qty_refund=3.0, to_refund=False)
        picking_return.move_line_ids.quantity = 3.0
        picking_return._action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 60.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered_return_no_refund_excess(self):
        """Delivered quantities exceed ordered quantities and return without refund"""
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = self._validate_so_picking(sale_order, qty_done=12.0)
        picking_return = self._create_return(picking, qty_refund=3.0, to_refund=False)
        picking_return.move_line_ids.quantity = 3.0
        picking_return._action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 120.0)
        self.assertEqual(order_line.margin_delivered_percent, 0.5)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered_precision(self):
        self.product.standard_price = 10.30
        self.product.list_price = 20.17
        sale_order = self._new_sale_order()
        sale_order.order_line[:1].discount = 17.0
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.quantity = 6.0
        picking.with_context(skip_backorder=True).button_validate()
        order_line = sale_order.order_line[:1]
        # price_subtotal is rounded
        self.assertEqual(order_line.price_subtotal, 100.45)
        # the unit reduce price will be computed as 100.45 / 6 = 16.741666666666667
        # it should not be rounded to 16.74
        # margin_delivered:
        # round(6 * ((100.45 /6) - 10.30)) != round(6 * (16.74 - 10.30))
        self.assertEqual(order_line.margin_delivered, 38.65)
        self.assertAlmostEqual(order_line.margin_delivered_percent, 0.38476854156296)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_no_cost(self):
        self.product.standard_price = 0.0
        self.product.list_price = 20
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.quantity = 6.0
        picking.with_context(skip_backorder=True).button_validate()
        order_line = sale_order.order_line[:1]
        # price_subtotal is rounded
        self.assertEqual(order_line.margin_delivered, 120)
        self.assertAlmostEqual(order_line.margin_delivered_percent, 1)
        self.assertEqual(order_line.purchase_price_delivery, order_line.purchase_price)
