# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product_margin.models.product_product import ProductProduct


class TestProductMarginAccumulatedLandedCost(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_avg = cls.env["product.category"].create(
            {
                "name": "Cat Test",
                "property_cost_method": "average",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Produtc Test",
                "detailed_type": "product",
                "categ_id": cls.category_avg.id,
                "company_id": cls.env.company.id,
            }
        )

    def test_compute_product_margin_fields_values(self):
        product = self.product
        super_result = {
            product.id: {
                "sale_num_invoiced": 10.0,
                "purchase_num_invoiced": 5.0,
                "total_cost": 50.0,
                "turnover": 200.0,
                "date_from": "2022-01-01",
                "date_to": "2022-12-31",
            }
        }
        fake_accumulated_cost = 100.0
        StockValuationAdjustmentLines = self.env["stock.valuation.adjustment.lines"]
        with patch.object(
            ProductProduct,
            "_compute_product_margin_fields_values",
            return_value=super_result,
        ):
            with patch.object(
                type(StockValuationAdjustmentLines),
                "_read_group",
                return_value=[(product, fake_accumulated_cost)],
            ):
                result = product._compute_product_margin_fields_values()
                self.assertEqual(
                    result[product.id]["accumulated_landed_costs"],
                    fake_accumulated_cost,
                )
                expected_avg_price = (
                    super_result[product.id]["total_cost"] + fake_accumulated_cost
                ) / super_result[product.id]["purchase_num_invoiced"]

                expected_margin = super_result[product.id]["turnover"] - (
                    super_result[product.id]["sale_num_invoiced"] * expected_avg_price
                )
                self.assertEqual(
                    result[product.id]["purchase_avg_price"],
                    expected_avg_price,
                )
                self.assertEqual(
                    result[product.id]["total_margin"],
                    expected_margin,
                )
