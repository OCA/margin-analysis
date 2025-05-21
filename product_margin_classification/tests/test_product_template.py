# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.tests.common import TransactionCase


# this is a copy of TestProductProduct, changed to work with product.template
# records.
class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.too_cheap = cls.env.ref(
            "product_margin_classification.too_cheap_product"
        ).product_tmpl_id
        cls.too_expensive = cls.env.ref(
            "product_margin_classification.too_expensive_product"
        ).product_tmpl_id
        cls.both = cls.too_cheap | cls.too_expensive

    def test_00_prices_not_equal(self):
        """A simple sanity check."""
        self.assertNotAlmostEqual(
            self.too_cheap.list_price,
            self.too_cheap.theoretical_price,
        )
        self.assertNotAlmostEqual(
            self.too_expensive.list_price,
            self.too_expensive.theoretical_price,
        )

    def test_01_action_apply_theoretical_price(self):
        action = self.env.ref(
            "product_margin_classification"
            ".action_product_template_apply_theoretical_price"
        )
        action.with_context(
            active_model="product.template",
            active_ids=self.both.ids,
        ).run()
        self.assertAlmostEqual(
            self.too_cheap.list_price,
            self.too_cheap.theoretical_price,
        )
        self.assertAlmostEqual(
            self.too_expensive.list_price,
            self.too_expensive.theoretical_price,
        )

    def test_02_action_apply_theoretical_price_too_cheap(self):
        action = self.env.ref(
            "product_margin_classification"
            ".action_product_template_apply_theoretical_price_too_cheap"
        )
        action.with_context(
            active_model="product.template",
            active_ids=self.both.ids,
        ).run()
        self.assertAlmostEqual(
            self.too_cheap.list_price,
            self.too_cheap.theoretical_price,
        )
        self.assertNotAlmostEqual(
            self.too_expensive.list_price,
            self.too_expensive.theoretical_price,
        )

    def test_03_action_apply_theoretical_price_too_expensive(self):
        action = self.env.ref(
            "product_margin_classification"
            ".action_product_template_apply_theoretical_price_too_expensive"
        )
        action.with_context(
            active_model="product.template",
            active_ids=self.both.ids,
        ).run()
        self.assertNotAlmostEqual(
            self.too_cheap.list_price,
            self.too_cheap.theoretical_price,
        )
        self.assertAlmostEqual(
            self.too_expensive.list_price,
            self.too_expensive.theoretical_price,
        )
