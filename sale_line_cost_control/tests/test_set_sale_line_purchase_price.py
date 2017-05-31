# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta
from .common import SaleCommon


class TestSetSaleLinePurchasePrice(SaleCommon):

    def test_set_purchase_price(self):
        sale = self._create_sale()
        line = sale.order_line[0]
        wizard = self.wizard_model.with_context(
            active_model='sale.order.line',
            active_id=line.id,
        ).create({})
        wizard.purchase_price = 15.
        wizard.confirm_purchase_price()
        self.assertEqual(15., line.purchase_price)


class TestChangeCostWithCurrency(SaleCommon):

    def _create_rate(self, currency, rate, days_ago=1):
        rate_date = datetime.now() - timedelta(days=days_ago)
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

    def test_set_purchase_price(self):
        sale = self._create_sale()
        line = sale.order_line[0]
        wizard = self.wizard_model.with_context(
            active_model='sale.order.line',
            active_id=line.id,
        ).create({})
        wizard.purchase_price = 30.
        wizard.currency_id = self.other_currency
        wizard.confirm_purchase_price()
        self.assertEqual(15., line.purchase_price)

    def test_set_purchase_price_past_date(self):
        self._create_rate(self.other_currency, 3.0, days_ago=10)
        sale = self._create_sale()
        sale.date_order = datetime.now() - timedelta(days=5)
        line = sale.order_line[0]
        wizard = self.wizard_model.with_context(
            active_model='sale.order.line',
            active_id=line.id,
        ).create({})
        wizard.purchase_price = 30.
        wizard.currency_id = self.other_currency
        wizard.confirm_purchase_price()
        self.assertEqual(10., line.purchase_price)
