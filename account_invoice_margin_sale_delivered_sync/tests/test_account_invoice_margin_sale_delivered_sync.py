# Copyright 2017-2018 Tecnativa - Sergio Teruel
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountInvoiceMarginSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "type": "sale", "code": "TEST_J"}
        )
        cls.account_type = cls.env["account.account.type"].create(
            {
                "name": "Test account type",
                "type": "receivable",
                "internal_group": "income",
            }
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
            {"name": "Test partner", "is_company": True}
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
        cls.product.property_account_income_id = cls.account
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
        self.sale_order.order_line.purchase_price_delivery = 300.00
        self.assertAlmostEqual(invoice.invoice_line_ids.purchase_price, 300.00, 2)
