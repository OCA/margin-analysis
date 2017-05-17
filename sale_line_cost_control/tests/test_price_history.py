# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import ProductCommon


class TestPriceHistory(ProductCommon):

    def _create_history_cost(self, product, date, cost):
        self.env['product.price.history'].create({
            'product_id': product.id,
            'company_id': self.company.id,
            'datetime': date,
            'cost': cost,
        })

    def test_multiple_price_same_date(self):
        date_cost = '2017-05-17 10:52:43'
        self._create_history_cost(self.product, date_cost, 15.0)
        self._create_history_cost(self.product, date_cost, 18.0)
        cost = self.product.get_history_price(
            self.company.id,
            date=date_cost,
        )
        self.assertEqual(18, cost)
