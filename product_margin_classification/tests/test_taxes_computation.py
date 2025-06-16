# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTaxesComputation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.percent_excluded_tax = cls.env["account.tax"].create(
            {
                "name": "percent excluded",
                "amount_type": "percent",
                "amount": 10,
                "price_include": False,
            }
        )
        cls.percent_included_tax = cls.env["account.tax"].create(
            {
                "name": "percent included",
                "amount_type": "percent",
                "amount": 10,
                "price_include": True,
                "include_base_amount": True,
            }
        )
        cls.fixed_excluded_tax = cls.env["account.tax"].create(
            {
                "name": "fixed excluded",
                "amount_type": "fixed",
                "amount": 1,
                "price_include": False,
            }
        )
        cls.fixed_included_tax = cls.env["account.tax"].create(
            {
                "name": "fixed included",
                "amount_type": "fixed",
                "amount": 1,
                "price_include": True,
            }
        )
        cls.test_product = cls.env["product.product"].create(
            {
                "name": "test product",
                "standard_price": 10,
                "list_price": 15,
                "margin_classification_id": cls.env.ref(
                    "product_margin_classification.classification_normal_margin"
                ).id,
            }
        )

    def test_percent_excluded_tax(self):
        self.test_product.taxes_id = [
            fields.Command.set([self.percent_excluded_tax.id])
        ]
        self.assertAlmostEqual(self.test_product.theoretical_price, 15)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(15)["total_excluded"], 15
        )

    def test_percent_included_tax(self):
        self.test_product.taxes_id = [
            fields.Command.set([self.percent_included_tax.id])
        ]
        self.assertAlmostEqual(self.test_product.theoretical_price, 16.5)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(16.5)["total_excluded"], 15
        )

    def test_fixed_excluded_tax(self):
        self.test_product.taxes_id = [fields.Command.set([self.fixed_excluded_tax.id])]
        self.assertAlmostEqual(self.test_product.theoretical_price, 15)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(15)["total_excluded"], 15
        )

    def test_fixed_included_tax(self):
        self.test_product.taxes_id = [fields.Command.set([self.fixed_included_tax.id])]
        self.assertAlmostEqual(self.test_product.theoretical_price, 16)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(16)["total_excluded"], 15
        )

    def test_percent_excluded_fixed_excluded_tax(self):
        self.test_product.taxes_id = [
            fields.Command.set(
                [self.percent_excluded_tax.id, self.fixed_excluded_tax.id]
            )
        ]
        self.assertAlmostEqual(self.test_product.theoretical_price, 15)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(15)["total_excluded"], 15
        )

    def test_percent_included_fixed_excluded_tax(self):
        self.test_product.taxes_id = [
            fields.Command.set(
                [self.percent_included_tax.id, self.fixed_excluded_tax.id]
            )
        ]
        self.assertAlmostEqual(self.test_product.theoretical_price, 16.5)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(16.5)["total_excluded"], 15
        )

    def test_percent_excluded_fixed_included_tax(self):
        self.test_product.taxes_id = [
            fields.Command.set(
                [self.percent_excluded_tax.id, self.fixed_included_tax.id]
            )
        ]
        self.assertAlmostEqual(self.test_product.theoretical_price, 16)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(16)["total_excluded"], 15
        )

    def test_percent_included_fixed_included_tax(self):
        self.test_product.taxes_id = [
            fields.Command.set(
                [self.percent_included_tax.id, self.fixed_included_tax.id]
            )
        ]
        self.assertAlmostEqual(self.test_product.theoretical_price, 17.5)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(17.5)["total_excluded"], 15
        )

    def test_include_base_amount_1(self):
        tax_1 = self.percent_included_tax.copy({"sequence": 1})
        tax_2 = self.percent_included_tax.copy({"sequence": 2})
        self.test_product.taxes_id = [fields.Command.set([tax_1.id, tax_2.id])]
        self.assertAlmostEqual(self.test_product.theoretical_price, 18.15)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(18.15)["total_excluded"], 15
        )

    def test_include_base_amount_2(self):
        tax_1 = self.percent_included_tax.copy(
            {"sequence": 1, "include_base_amount": False}
        )
        tax_2 = self.percent_included_tax.copy({"sequence": 2})
        self.test_product.taxes_id = [fields.Command.set([tax_1.id, tax_2.id])]
        self.assertAlmostEqual(self.test_product.theoretical_price, 18)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(18)["total_excluded"], 15
        )

    def test_include_base_amount_3(self):
        tax_1 = self.fixed_included_tax.copy(
            {"sequence": 1, "include_base_amount": True}
        )
        tax_2 = self.percent_included_tax.copy({"sequence": 2})
        self.test_product.taxes_id = [fields.Command.set([tax_1.id, tax_2.id])]
        self.assertAlmostEqual(self.test_product.theoretical_price, 17.6)
        self.assertAlmostEqual(
            self.test_product.taxes_id.compute_all(17.6)["total_excluded"], 15
        )

    def test_unsupported_tax_amount_type(self):
        division_tax = self.env["account.tax"].create(
            {
                "name": "division",
                "amount_type": "division",
                "amount": 10,
            }
        )
        with self.assertRaises(ValidationError):
            self.test_product.taxes_id = [fields.Command.set([division_tax.id])]
