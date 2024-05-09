# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        variant_group = cls.env.ref("product.group_product_variant")
        cls.user_variant = cls.env["res.users"].create(
            {"name": "variant", "login": "variant"}
        )
        variant_group.users = [fields.Command.link(cls.user_variant.id)]
        cls.user_no_variant = cls.env["res.users"].create(
            {"name": "no_variant", "login": "no_variant"}
        )
        variant_group.users = [fields.Command.unlink(cls.user_no_variant.id)]

        cls.picking_id = cls.env.ref("stock.incomming_shipment")
        cls.expected_view = cls.env.ref(
            "product_margin_classification.view_product_product_tree"
        )

    def test_view_variant(self):
        """When called from user with product variants, use our view."""
        result = self.picking_id.with_user(self.user_variant).action_view_products()
        self.assertEqual(
            result["views"], [(self.expected_view.id, "tree"), (False, "form")]
        )

    def test_view_no_variant(self):
        """When called from a user without product variants, don't use our view
        because it only supports product.product.
        """
        result = self.picking_id.with_user(self.user_no_variant).action_view_products()
        self.assertNotIn("views", result)
