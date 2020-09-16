# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestProductMarginClassification(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.too_expensive_product = self.env.ref(
            "product_margin_classification.too_expensive_product"
        )
        self.price_precision = self.env["decimal.precision"].precision_get(
            "Product Price"
        )
        self.classification_big_margin = self.env.ref(
            "product_margin_classification.classification_big_margin"
        )

    def test_01_product_use_theoretical_price(self):
        """Apply a 100% Markup (with rounding method) for a product with
        a standard price of 100. The result should be 199.95
        ((100 * (100 + 100) / 100) - 0.05)
        ((100 * (standard_price + markup) / 100) + price_surcharge)"""
        self.too_expensive_product.use_theoretical_price()

        new_price = round(
            self.too_expensive_product.list_price, self.price_precision
        )

        self.assertEquals(new_price, 199.95)

    def test_02_margin_apply_theoretical_price(self):
        """ Apply a margin for all the products of margin classification"""
        self.classification_big_margin.apply_theoretical_price()

        self.assertEquals(
            self.classification_big_margin.product_incorrect_price_qty, 0
        )

    def test_03_apply_markup_to_margin_classification(self):
        """ Apply markups to margin_classification"""
        # Apply correct markup, and check the result
        self.classification_big_margin.markup = 150
        self.assertEquals(
            self.classification_big_margin.profit_margin, 60
        )
        # Apply incorrect markup
        with self.assertRaises(ValidationError):
            self.classification_big_margin.markup = -100

    def test_04_apply_profit_margin_to_margin_classification(self):
        """ Apply profit margins to margin_classification"""
        # Apply correct profit margin, and check the result
        self.classification_big_margin.profit_margin = 90
        self.classification_big_margin._onchange_profit_margin()

        self.assertEquals(
            self.classification_big_margin.markup, 900
        )
        # Apply incorrect profit margin
        with self.assertRaises(ValidationError):
            self.classification_big_margin.profit_margin = 100
            self.classification_big_margin._onchange_profit_margin()

    def test_05_margin_classification_change_value(self):
        self.too_expensive_product.use_theoretical_price()

        # Change markup  and check theoritical_price
        theoritical_price = self.too_expensive_product.theoretical_price
        self.classification_big_margin.markup += 10
        self.assertNotEquals(
            theoritical_price, self.too_expensive_product.theoretical_price,
            "Change markup should change theoritical Price")

        # Change price_round and check theoritical_price
        theoritical_price = self.too_expensive_product.theoretical_price
        self.classification_big_margin.price_round += 10
        self.assertNotEquals(
            theoritical_price, self.too_expensive_product.theoretical_price,
            "Change price_round should change theoritical Price")

        # Change price_surcharge and check theoritical_price
        theoritical_price = self.too_expensive_product.theoretical_price
        self.classification_big_margin.price_surcharge += 10
        self.assertNotEquals(
            theoritical_price, self.too_expensive_product.theoretical_price,
            "Change price_surcharge should change theoritical Price")
