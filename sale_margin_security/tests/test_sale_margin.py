# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import AccessError
from odoo.tests import Form
from odoo.tests.common import new_test_user
from odoo.tools import mute_logger

from odoo.addons.sale.tests.common import SaleCommon


class SomethingCase(SaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product.standard_price = 10
        cls.salesperson_edit = new_test_user(
            cls.env,
            name="Salesperson PC Edit",
            login="salesperson_edit",
            groups=(
                "sales_team.group_sale_salesman,"
                "product_cost_security.group_product_edit_cost"
            ),
        )
        cls.salesperson_read = new_test_user(
            cls.env,
            name="Salesperson PC Read",
            login="salesperson_read",
            groups="sales_team.group_sale_salesman,product_cost_security.group_product_cost",
        )
        cls.salesperson_none = new_test_user(
            cls.env,
            name="Salesperson PC None",
            login="salesperson_none",
            groups="sales_team.group_sale_salesman",
        )

    def test_rw_margin_access(self):
        """Unauthorized users cannot see margin data."""
        self.empty_order.user_id = self.salesperson_edit
        so = self.empty_order.with_user(self.salesperson_edit)
        with Form(so) as order_f:
            # Lines contain margin fields
            with order_f.order_line.new() as line_f:
                line_f.product_id = self.product
                self.assertEqual(line_f.purchase_price, 10)
                self.assertEqual(line_f.margin, 10)
                self.assertEqual(line_f.margin_percent, 0.5)
                # Editor can change purchase price
                line_f.purchase_price = 15
                self.assertEqual(line_f.margin, 5)
                self.assertEqual(line_f.margin_percent, 0.25)
            # View contains margin fields, which are computed and readonly upstream
            self.assertEqual(order_f.margin, 5)
            self.assertEqual(order_f.margin_percent, 0.25)
        # Can read those fields trough the API
        so.read(["margin", "margin_percent"])
        so.order_line.read(["purchase_price", "margin", "margin_percent"])

    def test_ro_margin_access(self):
        """Unauthorized users cannot see margin data."""
        self.empty_order.user_id = self.salesperson_read
        so = self.empty_order.with_user(self.salesperson_read)
        with Form(so) as order_f:
            # Lines contain margin fields
            with order_f.order_line.new() as line_f:
                line_f.product_id = self.product
                line_f.product_uom_qty = 1
                self.assertEqual(line_f.purchase_price, 10)
                self.assertEqual(line_f.margin, 10)
                self.assertEqual(line_f.margin_percent, 0.5)
                # Editor cannot change purchase price
                with self.assertRaises(AssertionError):
                    line_f.purchase_price = 10
            # View contains margin fields, which are computed and readonly upstream
            self.assertEqual(order_f.margin, 10)
            self.assertEqual(order_f.margin_percent, 0.5)
        # Can read those fields trough the API
        so.read(["margin", "margin_percent"])
        so.order_line.read(["purchase_price", "margin", "margin_percent"])

    @mute_logger("odoo.models")
    def test_no_margin_access(self):
        """Unauthorized users cannot see margin data."""
        self.empty_order.user_id = self.salesperson_none
        so = self.empty_order.with_user(self.salesperson_none)
        with Form(so) as order_f:
            # View doesn't contain margin fields
            self.assertRaises(AssertionError, hasattr, order_f, "margin")
            self.assertRaises(AssertionError, hasattr, order_f, "margin_percent")
            # Lines don't contain margin fields
            with order_f.order_line.new() as line_f:
                line_f.product_id = self.product
                self.assertRaises(AssertionError, hasattr, line_f, "purchase_price")
                self.assertRaises(AssertionError, hasattr, line_f, "margin")
                self.assertRaises(AssertionError, hasattr, line_f, "margin_percent")
        # This user cannot read those fields trough the API
        self.assertRaises(AccessError, so.read, ["margin"])
        self.assertRaises(AccessError, so.read, ["margin_percent"])
        self.assertRaises(AccessError, so.order_line.read, ["purchase_price"])
        self.assertRaises(AccessError, so.order_line.read, ["margin"])
        self.assertRaises(AccessError, so.order_line.read, ["margin_percent"])
