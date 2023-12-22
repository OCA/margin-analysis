# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestAccountInvoiceMargin(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.product_a.lst_price = 200
        cls.product_a.standard_price = 100
        cls.invoice = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            invoice_date=fields.Date.from_string("2017-06-19"),
            post=False,
            products=cls.product_a,
        )
        cls.invoice.invoice_line_ids.quantity = 10
        cls.vendor_bill = cls.init_invoice(
            "in_invoice",
            partner=cls.partner_a,
            invoice_date=fields.Date.from_string("2017-06-19"),
            post=False,
            products=cls.product_a,
        )
        cls.vendor_bill.invoice_line_ids.quantity = 10

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
            .create(
                {
                    "reason": "reason test create",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        action = wiz.refund_moves()
        new_invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(new_invoice.invoice_line_ids.margin, 1000.00)
        self.assertEqual(new_invoice.invoice_line_ids.margin_signed, -1000.00)

    def test_invoice_modify_moves(self):
        self.invoice.action_post()
        wiz = (
            self.env["account.move.reversal"]
            .with_context(
                active_model="account.move",
                active_ids=self.invoice.ids,
                active_id=self.invoice.id,
            )
            .create(
                {
                    "reason": "reason test create",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        action = wiz.modify_moves()
        new_invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(new_invoice.invoice_line_ids.margin, 1000.00)
        self.assertEqual(new_invoice.invoice_line_ids.margin_signed, 1000.00)

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
        move_form.partner_id = self.partner_a
        move_form.currency_id = currency
        move_form.invoice_date = "2022-01-01"
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_a
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_line_ids.purchase_price, 200)

    def test_invoice_payment_register(self):
        invoice = self.invoice.copy()
        invoice.action_post()
        self.assertEqual(invoice.margin, 1000.0)
        self.assertEqual(invoice.margin_signed, 1000.0)
        self.assertEqual(invoice.margin_percent, 50.0)
        payments = (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=invoice.ids,
            )
            .create(
                {
                    "group_payment": False,
                }
            )
            ._create_payments()
        )
        self.assertEqual(1, len(payments))
        self.assertTrue(payments.move_id)
        self.assertFalse(payments.move_id.is_invoice())
        self.assertEqual(payments.move_id.amount_total, invoice.amount_total)
        self.assertEqual(payments.move_id.margin, 0.0)
        self.assertEqual(payments.move_id.margin_signed, 0.0)
        self.assertEqual(payments.move_id.margin_percent, 0.0)
