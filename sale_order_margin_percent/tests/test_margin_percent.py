#  Copyright 2019  Camptocamp SA
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from odoo.tests import SavepointCase


class TestSaleMarginPercent(SavepointCase):

    def setUp(self):
        super().setUp()
        self.SaleOrder = self.env['sale.order']

        self.product_uom_id = self.ref('uom.product_uom_unit')
        self.product_id = self.ref('product.product_product_24')
        self.partner_id = self.ref('base.res_partner_4')

    def test_sale_margin(self):
        """ Test the sale_margin module in Odoo. """
        sale_order = self.SaleOrder.create({
            'name': 'Test_SO011',
            'order_line': [
                (0, 0, {
                    'name': '[CARD] Graphics Card',
                    'purchase_price': 700.0,
                    'price_unit': 1000.0,
                    'product_uom': self.product_uom_id,
                    'product_uom_qty': 10.0,
                    'state': 'draft',
                    'product_id': self.product_id}),
                ],
            'partner_id': self.partner_id,
            })

        # (1000 - 700)*10 = 3000 - margin
        # 1000 * 10 = 10000      - amount untaxed
        self.assertEqual(sale_order.percent, 30.00)

        sale_order.order_line.price_unit = 1200
        sale_order._amount_all()
        # (1200 - 700)*10 = 5000 - margin
        # 1000 * 10 = 12000      - amount untaxed
        self.assertEqual(sale_order.percent, 41.67)
