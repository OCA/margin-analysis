# Copyright 2017-2018 Tecnativa - Sergio Teruel
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("-at_install", "post_install")
class TestAccountInvoiceMargin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "type": "sale", "code": "TEST_J"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TESTACCRECV",
                "account_type": "asset_receivable",
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
                "invoice_policy": "order",
                "list_price": 200.00,
                "standard_price": 100.00,
            }
        )
        pricelist = cls.env["product.pricelist"].create({"name": "Public Pricelist"})

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_invoice_sale_order(self):
        self.sale_order.action_confirm()
        self.sale_order.order_line.purchase_price = 500.00
        invoice = self.sale_order._create_invoices()
        self.assertAlmostEqual(invoice.invoice_line_ids.purchase_price, 500.00, 2)

    def test_invoice_down_payment(self):
        SaleAdvancePaymentInv = self.env["sale.advance.payment.inv"]
        AccountMove = self.env["account.move"]
        product = self.env["product.product"].create(
            {
                "name": "test product for down payment",
                "categ_id": self.product_categ.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "list_price": 1000.00,
                "standard_price": 500.00,
                "type": "service",
                "invoice_policy": "order",
            }
        )
        self.order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": product.id,
                            "name": "Testing Product",
                            "product_uom_qty": 1,
                            "product_uom": product.uom_id.id,
                            "price_unit": 1000.00,
                            "purchase_price": 500.00,
                        },
                    ),
                ],
            }
        )
        self.order.action_confirm()
        # Create one down payment
        wiz = SaleAdvancePaymentInv.with_context(
            active_ids=self.order.ids,
            open_invoices=True,
        ).create({"advance_payment_method": "fixed", "fixed_amount": 100.00})
        action = wiz.create_invoices()
        invoice_id = action["res_id"]
        invoice1 = AccountMove.browse(invoice_id)
        self.assertEqual(invoice1.margin, 0.0)

        # Create regular invoice which has a down payment
        wiz = SaleAdvancePaymentInv.with_context(
            active_ids=self.order.ids,
            open_invoices=True,
        ).create({"advance_payment_method": "delivered"})
        wiz.create_invoices()
        invoice2 = self.order.invoice_ids - invoice1
        self.assertEqual(invoice2.margin, 500.00)
        self.assertEqual(invoice2.margin_percent, 50.0)
