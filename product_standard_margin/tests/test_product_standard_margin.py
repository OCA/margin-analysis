# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProductStandardMargin(common.TransactionCase):

    def setUp(self):
        super(TestProductStandardMargin, self).setUp()
        self.non_profit_wine = self.env.ref(
            'product_standard_margin.product_non_profit_wine')
        self.free_wine = self.env.ref(
            'product_standard_margin.product_free_wine')
        self.wine = self.env.ref(
            'product_standard_margin.product_wine')

    def test_01_non_profit_product_margin(self):
        """Check margin of a non-profit product margin"""
        self.assertEquals(self.non_profit_wine.standard_margin, 0)
        self.assertEquals(self.non_profit_wine.standard_margin_rate, 0)

    def test_02_free_product_margin(self):
        """Check margin of a non-profit product margin"""
        self.assertEquals(self.free_wine.standard_margin, -10.0)
        self.assertEquals(self.free_wine.standard_margin_rate, 999.0)

    def test_03_product_margin_with_currency(self):
        """Check margin with currency_id in context"""
        currency_id = self.env.ref('base.EUR').id

        self.wine.with_context(currency_id=currency_id).write({
            'standard_price': 7.0})

        self.assertEquals(self.wine.standard_margin, 3.0)
