# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestAccountInvoiceMargin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMargin, cls).setUpClass()
        cls.Product = cls.env["product.template"]

        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "type": "sale", "code": "TEST_J"}
        )
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test account type", "type": "other", "internal_group": "income"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST_A",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "customer_rank": 1, "is_company": True}
        )
        cls.partner.property_account_receivable_id = cls.account
        cls.product_categ = cls.env["product.category"].create(
            {"name": "Test category"}
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "categ_id": cls.product_categ.id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "test-margin",
                "list_price": 200.00,
                "standard_price": 100.00,
            }
        )
        cls.product.property_account_income_id = cls.account
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.from_string("2017-06-19"),
                "move_type": "out_invoice",
                "currency_id": cls.env.user.company_id.currency_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "account_id": cls.product.property_account_income_id.id,
                            "name": "Test Margin",
                            "price_unit": cls.product.list_price,
                            "quantity": 10,
                            "purchase_price": cls.product.standard_price,
                        },
                    )
                ],
            }
        )
        cls.vendor_bill = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.from_string("2017-06-19"),
                "move_type": "in_invoice",
                "currency_id": cls.env.user.company_id.currency_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "account_id": cls.product.property_account_income_id.id,
                            "name": "Test Margin",
                            "price_unit": cls.product.list_price,
                            "quantity": 10,
                        },
                    )
                ],
            }
        )

    def test_invoice_margin(self):
        self.assertEqual(self.invoice.invoice_line_ids.purchase_price, 100.00)
        self.assertEqual(self.invoice.invoice_line_ids.margin, 1000.00)

        self.invoice.invoice_line_ids.with_context(
            check_move_validity=False
        ).discount = 50
        self.assertEqual(self.invoice.invoice_line_ids.margin, 0.0)

    def test_vendor_bill_margin(self):
        self.assertEqual(self.vendor_bill.invoice_line_ids.purchase_price, 0.00)
        self.assertEqual(self.vendor_bill.invoice_line_ids.margin, 0.00)

    def test_invoice_margin_uom(self):
        inv_line = self.invoice.invoice_line_ids
        inv_line.update({"product_uom_id": self.env.ref("uom.product_uom_dozen").id})
        inv_line.with_context(check_move_validity=False)._onchange_uom_id()
        self.assertEqual(inv_line.margin, 12000.00)

    def test_invoice_refund(self):
        self.invoice.action_post()
        wiz = (
            self.env["account.move.reversal"]
            .with_context(
                active_model="account.move",
                active_ids=self.invoice.ids,
                active_id=self.invoice.id,
            )
            .create({"refund_method": "refund", "reason": "reason test create"})
        )
        action = wiz.reverse_moves()
        new_invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(new_invoice.invoice_line_ids.margin, 1000.00)
        self.assertEqual(new_invoice.invoice_line_ids.margin_signed, -1000.00)

    def test_invoice_different_currency(self):
        company = self.env.company
        currency = self.env["res.currency"].create(
            {
                "name": "TC1",
                "symbol": "T",
                "rate_ids": [
                    (0, 0, {"company_id": company.id, "name": "2022-01-01", "rate": 2})
                ],
            }
        )
        company.currency_id.rate_ids.unlink()  # avoid odd rates if currency != EUR
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner
        move_form.currency_id = currency
        move_form.invoice_date = "2022-01-01"
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_line_ids.purchase_price, 200)
