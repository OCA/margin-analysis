# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import SaleCommon


class TestSalePurchasePriceMissing(SaleCommon):

    def test_line_no_cost_at_creation(self):
        sale = self._create_sale()
        for line in sale.order_line:
            self.assertTrue(line.purchase_price_missing)

    def test_line_cost_at_creation(self):
        for product in self.products.values():
            product.standard_price = 10.
        sale = self._create_sale()
        for line in sale.order_line:
            self.assertFalse(line.purchase_price_missing)

    def test_line_cost_added_after_creation(self):
        sale = self._create_sale()
        sale.order_line.write({'purchase_price': 10.})
        for line in sale.order_line:
            self.assertFalse(line.purchase_price_missing)

    def test_line_cost_removed_after_creation(self):
        for product in self.products.values():
            product.standard_price = 10.
        sale = self._create_sale()
        sale.order_line.write({'purchase_price': 0})
        for line in sale.order_line:
            self.assertTrue(line.purchase_price_missing)
