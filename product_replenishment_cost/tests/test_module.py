# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        self.ProductProduct = self.env['product.product']

    # Test Section
    def test_create_or_update(self):
        # Test compute on creation
        product = self.ProductProduct.create({
            'name': 'Wine A01',
            'standard_price': 50,
        })
        self.assertEqual(product.replenishment_cost, 50.0)

        # Test Update
        product.standard_price = 70.0

        self.assertEqual(product.replenishment_cost, 70.0)

        # Test Update via template
        product.product_tmpl_id.standard_price = 100.0
        self.assertEqual(product.replenishment_cost, 100.0)
