# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestRepairMargin(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestRepairMargin, cls).setUpClass()
        cls.Product = cls.env['product.template']

        cls.journal = cls.env["account.journal"].create({
            "name": "Test journal",
            "type": "sale",
            "code": "TEST_J",
        })
        cls.account_type = cls.env["account.account.type"].create({
            "name": "Test account type",
            "type": "receivable",
        })
        cls.account = cls.env["account.account"].create({
            "name": "Test account",
            "code": "TEST_A",
            "user_type_id": cls.account_type.id,
            "reconcile": True,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Test partner",
            "customer": True,
            "is_company": True,
        })
        cls.partner.property_account_receivable_id = cls.account
        cls.product_categ = cls.env["product.category"].create({
            "name": "Test category"
        })

        cls.product = cls.env["product.product"].create({
            "name": "test product",
            "categ_id": cls.product_categ.id,
            "uom_id": cls.env.ref('uom.product_uom_unit').id,
            "uom_po_id": cls.env.ref('uom.product_uom_unit').id,
            "default_code": "test-margin",
            "list_price": 200.00,
            "standard_price": 100.00,
        })
        cls.product.property_account_receivable_id = cls.account
        cls.product1 = cls.env.ref('product.product_product_25')
        cls.repair = cls.env['repair.order'].create({
            'name': 'Test Repair',
            'product_id': cls.product1.id,
            'product_uom': cls.product1.uom_id.id,
            'partner_id': cls.partner.id,
            'product_qty': 1,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'operations': [
                (0, 0, {
                    'product_id': cls.product.id,
                    'type': 'add',
                    'name': 'Test Margin',
                    'price_unit': cls.product.list_price,
                    'product_uom_qty': 10,
                    'product_uom': cls.product.uom_id.id,
                    'purchase_price': cls.product.standard_price,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.env.ref('stock.location_production').id,
                })],
        })

    def test_repair_margin(self):
        self.assertEqual(self.repair.operations.purchase_price, 100.00)
        self.assertEqual(self.repair.operations.margin, 1000.00)

    def test_repair_margin_uom(self):
        operations = self.repair.operations
        operations.write({
            'product_uom': self.env.ref('uom.product_uom_dozen').id,
        })
        operations._onchange_product_uom()
        operations._onchange_product_id_repair_margin()
        self.assertEqual(operations.margin, 12000.00)
