# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestReportProductMarginCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
