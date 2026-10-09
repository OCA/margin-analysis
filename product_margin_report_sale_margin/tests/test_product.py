# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.product_margin.models.product_product import ProductProduct

from .test_common import TestReportProductMarginCommon


class TestReportProductMargin(TestReportProductMarginCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.Product.create(
            {
                "name": "Test Product",
            }
        )

    def test_compute_product_margin_fields_values(self):
        mocked_super_return = {
            self.product.id: {
                "turnover": 1000.0,
                "sale_num_invoiced": 10.0,
                "purchase_avg_price": 50.0,
            }
        }

        with patch.object(
            ProductProduct,
            "_compute_product_margin_fields_values",
            return_value=mocked_super_return,
        ):
            result = self.product._compute_product_margin_fields_values()

            sales_margin = 1000.0 - (10.0 * 50.0)
            sales_margin_rate = (sales_margin * 100) / 1000.0

            self.assertEqual(result[self.product.id]["sales_margin"], sales_margin)
            self.assertEqual(
                result[self.product.id]["sales_margin_rate"], sales_margin_rate
            )
