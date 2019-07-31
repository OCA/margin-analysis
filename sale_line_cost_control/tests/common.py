# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.addons.sale.tests import test_sale_common


class SaleCommon(test_sale_common.TestSale):

    def setUp(self):
        super(SaleCommon, self).setUp()
        self.wizard_model = self.env['set.sale.line.purchase.price']
        for product in self.products.values():
            product.standard_price = 0

        self.company = self.env.ref('base.main_company')
        self.base_currency = self.env.ref('base.EUR')
        # Set company currency by SQL to avoid error 'You cannot change the
        # currency of the company since some journal items already exist'
        self.env.cr.execute("""
            UPDATE res_company
            SET currency_id = %s
            WHERE id = %s
        """, (
            self.company.id,
            self.base_currency.id
        ))

    def _create_sale(self):
        sale = self.env['sale.order'].sudo(self.user).create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.products.iteritems()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        return sale
