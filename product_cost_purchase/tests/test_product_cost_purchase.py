# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Numérigraphe SARL.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase

from openerp import netsvc


class TestProductCostPurchase(TransactionCase):

    def setUp(self):

        def ref(module, value):
            return self.registry('ir.model.data').get_object_reference(
                self.cr, self.uid, module, value)[1]

        super(TestProductCostPurchase, self).setUp()
        self.product_obj = self.registry('product.product')
        self.po_obj = self.registry('purchase.order')
        self.po_line_obj = self.registry('purchase.order.line')
        # Get a product without Purchases
        self.product0_id = self.registry('ir.model.data').get_object_reference(
            self.cr, self.uid, 'product', 'product_product_24')[1]
        # Get a product with a BoM
        self.product1_id = ref('product', 'product_product_18')
        # Get UoMs
        self.unit_id = ref('product', 'product_uom_unit')
        self.dozen_id = ref('product', 'product_uom_dozen')
        # Get a supplier
        self.supplier_id = ref('base', 'res_partner_3')
        # Get a stock location for the purchase order
        self.location_id = ref('stock', 'stock_location_3')

    # Emulate client-side onchange
    def change_partner(self):
        """Call the client-side onchange for supplier"""
        self.po_data.update(self.po_obj.onchange_partner_id(
            self.cr, self.uid, None,
            self.po_data.get('partner_id'))['value'])

    def change_product(self):
        """Call the client-side onchange for product & uom"""
        self.po_line_data.update(self.po_line_obj.onchange_product_id(
            self.cr, self.uid, None,
            self.po_data.get('pricelist_id'),
            self.po_line_data.get('product_id'),
            self.po_line_data.get('product_qty'),
            self.po_line_data.get('product_uom'),
            self.po_data.get('partner_id'),
            self.po_data.get('date_order'),
            self.po_data.get('fiscal_position'),
            self.po_data.get('date_planned'),
            self.po_line_data.get('name'),
            self.po_line_data['price_unit'])['value'])

    def change_uom(self):
        self.po_line_data.update(self.po_line_obj.onchange_product_uom(
            self.cr, self.uid, None,
            self.po_data.get('pricelist_id'),
            self.po_line_data.get('product_id'),
            self.po_line_data.get('product_qty'),
            self.po_line_data.get('product_uom'),
            self.po_data.get('partner_id'),
            self.po_data.get('date_order'),
            self.po_data.get('fiscal_position'),
            self.po_data.get('date_planned'),
            self.po_line_data.get('name'),
            self.po_line_data['price_unit'])['value'])

    def test_10_purchase(self):
        """Test replenishment price updates

        The replenishment price must match the Cost Price if the product has
        no PO and no BoM.
        It must match the PO's price if the product has
        a PO, whether it has a BoM or not.
        It must not change if the PO's UoM is changed.
        """
        cr = self.cr
        uid = self.uid
        # get the current costs of the products
        products = self.product_obj.browse(
            cr, uid, [self.product0_id, self.product1_id])
        initial_costs = [p.cost_price for p in products]

        # change the cost price for 1st product
        self.product_obj.write(
            cr, uid, self.product0_id, {'standard_price': 123.45})
        # check that the repl. cost matches the cost price
        products[0].refresh()
        self.assertEqual(products[0].cost_price, 123.45)

        # record a purchase quotation for a random price for 1st product
        self.po_data = {'partner_id': self.supplier_id,
                        'location_id': self.location_id}
        self.change_partner()
        po_id = self.po_obj.create(cr, uid, self.po_data)
        self.po_line_data = {'order_id': po_id,
                             'product_id': self.product0_id,
                             'product_qty': 12000.0,
                             'product_uom': self.unit_id,
                             'price_unit': 234.56}
        self.change_product()
        po_line_id = self.po_line_obj.create(cr, uid, self.po_line_data)
        # check that the cost is the same as the purchase order's
        products[0].refresh()
        self.assertEqual(products[0].cost_price, 234.56)

        # change the quotation line's UoM to Dozen
        self.po_line_data['product_uom'] = self.dozen_id
        self.change_uom()
        self.po_line_obj.write(cr, uid, po_line_id, self.po_line_data)
        # check that the cost is unchanged
        products[0].refresh()
        self.assertEqual(products[0].cost_price, 234.56)

        # change the product to a product with a BoM
        self.po_line_data['product_id'] = self.product1_id
        self.change_product()
        po_line_id = self.po_line_obj.create(cr, uid, self.po_line_data)
        # check that the cost of the old product is back to the initial value
        products[0].refresh()
        self.assertEqual(products[0].cost_price, 123.45)
        # check that the cost of the new product is the same as the PO's
        products[1].refresh()
        self.assertEqual(products[1].cost_price, 234.56)

        # cancel the purchase order
# This does not work in v7 because the line's state is not updated
# TODO uncomment in v8
#         netsvc.LocalService("workflow").trg_validate(
#             uid, 'purchase.order', po_id, 'purchase_cancel', cr)
#         # Check that the cost is back to the initial value
#         products[1].refresh()
#         self.assertEqual(products[1].cost_price, initial_costs[1])
