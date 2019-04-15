#  Copyright 2019 Tecnativa - Sergio Teruel
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from datetime import datetime
from odoo.tests import SavepointCase


class TestSaleMarginCostExtra(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.product_uom_id = cls.env.ref('product.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'type': 'product',
            'uom_id': cls.product_uom_id.id,
            'standard_price': 10.0,
            'list_price': 20.00,
            'tracking': 'none',
        })
        cls.src_location = cls.env.ref('stock.stock_location_stock')
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Test pricelist',
            'item_ids': [(0, 0, {
                'applied_on': '3_global',
                'compute_price': 'formula',
                'base': 'list_price',
            })]
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'partner test',
            'property_product_pricelist': cls.pricelist.id,
        })
        cls.quant = cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.src_location.id,
            'quantity': 100.0,
        })

    def _new_sale_order(self):
        sale_order = self.SaleOrder.new({
            'date_order': datetime.today(),
            'name': 'Test_SO011',
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 6,
                })
            ],
            'partner_id': self.partner.id,
        })
        sale_order.onchange_partner_id()
        return self.SaleOrder.create(
            sale_order._convert_to_write(sale_order._cache))

    def test_sale_margin_ordered(self):
        sale_order = self._new_sale_order()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 60.0)
        self.assertEqual(order_line.margin_delivered_percent, 50.0)
        self.assertEqual(
            order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_delivered(self):
        sale_order = self._new_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.qty_done = 3.0
        picking.action_done()
        order_line = sale_order.order_line[:1]
        self.assertEqual(order_line.margin_delivered, 30.0)
        self.assertEqual(order_line.margin_delivered_percent, 50.0)
        self.assertEqual(
            order_line.purchase_price_delivery, order_line.purchase_price)

    def test_sale_margin_zero(self):
        sale_order = self._new_sale_order()
        order_line = sale_order.order_line[:1]
        order_line.product_uom_qty = 0.0
        self.assertEqual(order_line.margin_delivered, 0.0)
        self.assertEqual(order_line.margin_delivered_percent, 0)
