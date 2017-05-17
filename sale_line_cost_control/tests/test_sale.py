# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import SaleCommon


class TestSaleCostMissing(SaleCommon):

    def test_line_no_cost_at_creation(self):
        sale = self._create_sale()
        for line in sale.order_line:
            self.assertTrue(line.cost_missing)

    def test_line_cost_at_creation(self):
        for product in self.products.values():
            product.standard_price = 10.
        sale = self._create_sale()
        for line in sale.order_line:
            self.assertFalse(line.cost_missing)

    def test_line_cost_added_after_creation(self):
        sale = self._create_sale()
        for product in self.products.values():
            product.standard_price = 10.
        for line in sale.order_line:
            self.assertFalse(line.cost_missing)

    def test_line_cost_removed_after_creation(self):
        for product in self.products.values():
            product.standard_price = 10.
        sale = self._create_sale()
        for product in self.products.values():
            product.standard_price = 0.
        for line in sale.order_line:
            self.assertTrue(line.cost_missing)


class TestSaleLineStandardPrice(SaleCommon):

    def test_line_no_cost_at_creation(self):
        sale = self._create_sale()
        for line in sale.order_line:
            self.assertEquals(0, line.product_standard_price)

    def test_line_cost_at_creation(self):
        for product in self.products.values():
            product.standard_price = 10.
        sale = self._create_sale()
        for line in sale.order_line:
            self.assertEquals(10., line.product_standard_price)

    def test_line_cost_added_after_creation(self):
        sale = self._create_sale()
        for product in self.products.values():
            product.standard_price = 10.
        for line in sale.order_line:
            self.assertEquals(10., line.product_standard_price)

    def test_line_cost_removed_after_creation(self):
        for product in self.products.values():
            product.standard_price = 10.
        sale = self._create_sale()
        for product in self.products.values():
            product.standard_price = 0.
        for line in sale.order_line:
            self.assertEquals(0, line.product_standard_price)
