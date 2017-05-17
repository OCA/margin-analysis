# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta
from .common import SaleCommon, ProductCommon


class TestChangeProductCost(ProductCommon):

    def test_set_cost(self):
        wizard = self.env['change.product.cost'].create({
            'product_id': self.product.id,
            'standard_price': 15.,
            'currency_id': self.base_currency.id,
        })
        wizard.confirm_cost()
        self.assertEqual(15., self.product.standard_price)

    def test_default_cost(self):
        self.product.standard_price = 15.
        wizard = self.env['change.product.cost'].with_context(
            default_product_id=self.product.id,
            default_currency_id=self.base_currency.id).create({})
        self.assertEqual(15., wizard.standard_price)

    def test_onchange_cost(self):
        product2 = self.env['product.product'].create({'name': 'product2'})
        self.product.standard_price = 15.

        wizard = self.env['change.product.cost'].with_context(
            default_product_id=product2,
            default_currency_id=self.base_currency.id).create({})
        self.assertEqual(0, wizard.standard_price)

        wizard.product_id = self.product
        wizard.onchange_product_id()
        self.assertEqual(15.0, wizard.standard_price)


class TestActionSaleLine(SaleCommon):

    def test_action(self):
        sale = self._create_sale()
        line = sale.order_line[0]
        action = line.action_add_cost_on_product()
        expected = {
            'product_readonly': True,
            'default_product_id': line.product_id.id,
            'default_currency_id': sale.currency_id.id,
        }
        self.assertEqual(expected, action['context'])


class TestChangeCostWithCurrency(ProductCommon):

    def _create_rate(self, currency, rate):
        rate_date = datetime.now() - timedelta(days=1)
        self.env['res.currency.rate'].create({
            'name': rate_date,
            'company_id': self.company.id,
            'currency_id': currency.id,
            'rate': rate,
        })

    def setUp(self):
        super(TestChangeCostWithCurrency, self).setUp()
        self.other_currency = self.env.ref('base.CHF')
        self._create_rate(self.base_currency, 1.0)
        self._create_rate(self.other_currency, 2.0)

    def test_set_cost(self):
        wizard = self.env['change.product.cost'].create({
            'product_id': self.product.id,
            'standard_price': 30.,
            'currency_id': self.other_currency.id,
        })
        wizard.confirm_cost()
        self.assertEqual(15., self.product.standard_price)
