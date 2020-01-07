# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ProductProduct = self.env['product.product']
        self.ProductTemplate = self.env['product.template']

    # Custom Section
    def _create_product(self, model, standard_price, sale_price, sale_tax_ids):
        if model == 'product':
            ModelObj = self.ProductProduct
        else:
            ModelObj = self.ProductTemplate
        return ModelObj.create({
            'name': 'Demo Product',
            'standard_price': standard_price,
            'lst_price': sale_price,
            'taxes_id': [(6, 0, sale_tax_ids)],
        })

    # Test Section
    def test_01_classic_margin(self):
        for model in ['product', 'template']:
            product = self._create_product(model, 50, 200, [])
            self.assertEqual(
                product.standard_margin, 150,
                "Incorrect Standard Margin")
            self.assertEqual(
                product.standard_margin_rate, 75.0,
                "Incorrect Standard Margin Rate")

    def test_02_margin_without_standard_price(self):
        for model in ['product', 'template']:
            product = self._create_product(model, 0, 200, [])
            self.assertEqual(
                product.standard_margin, 200,
                "Incorrect Standard Margin (without standard price)")
            self.assertEqual(
                product.standard_margin_rate, 100.0,
                "Incorrect Standard Margin Rate (without standard price)")

    def test_03_margin_without_sale_price(self):
        for model in ['product', 'template']:
            product = self._create_product(model, 50, 0, [])
            self.assertEqual(
                product.standard_margin, -50,
                "Incorrect Standard Margin (without sale price)")
            self.assertEqual(
                product.standard_margin_rate, 999.0,
                "Incorrect Standard Margin Rate (without sale price)")
