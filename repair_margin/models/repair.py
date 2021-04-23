# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    currency_id = fields.Many2one(
        "res.currency",
        related='pricelist_id.currency_id',
        string="Currency",
        readonly=True,
        required=True)
    margin = fields.Monetary(
        string='Margin',
        compute='_compute_margin',
        digits=dp.get_precision('Product Price'),
        store=True,
        currency_field='currency_id',
    )
    margin_percent = fields.Float(
        string='Margin (%)',
        digits=dp.get_precision('Product Price'),
        compute='_compute_margin',
        store=True,
    )

    @api.multi
    @api.depends(
        'operations.margin',
        'operations.price_subtotal',
    )
    def _compute_margin(self):
        real_repairs = self.filtered(
            lambda x: not isinstance(x.id, models.NewId))
        virtual_repairs = self - real_repairs
        chunks = (
            real_repairs[i:i + models.PREFETCH_MAX]
            for i in range(0, len(real_repairs), models.PREFETCH_MAX)
        )
        # split in chunks for not losing performance in IN SQL query
        for chunk in chunks:
            # quick computation with read_group for real DB records
            res = self.env['repair.line'].read_group(
                [('repair_id', 'in', chunk.ids)],
                ['margin', 'price_subtotal'],
                ['repair_id'],
            )
            for group in res:
                repair = self.browse(group['repair_id'][0])
                repair.update({
                    'margin': group['margin'],
                    'margin_percent': (
                        group['price_subtotal'] and
                        group['margin'] / group['price_subtotal'] * 100 or 0
                    ),
                })
        # Normal computation for virtual IDs
        for repair in virtual_repairs:
            repair_lines = repair.operations
            price_subtotal = sum(repair_lines.mapped('price_subtotal'))
            margin = sum(repair_lines.mapped('margin'))
            repair.update({
                'margin': sum(repair_lines.mapped('margin')),
                'margin_percent': price_subtotal and (
                    margin / price_subtotal * 100) or 0,
            })


class RepairLine(models.Model):
    _inherit = 'repair.line'

    margin = fields.Float(
        compute='_compute_margin',
        digits=dp.get_precision('Product Price'),
        store=True,
        string='Margin',
    )
    margin_percent = fields.Float(
        string='Margin (%)',
        compute='_compute_margin',
        store=True,
        readonly=True,
    )
    purchase_price = fields.Float(
        digits=dp.get_precision('Product Price'),
        string='Cost',
    )

    @api.depends('purchase_price', 'price_subtotal')
    def _compute_margin(self):
        for line in self.filtered(lambda x: x.type == 'add'):
            tmp_margin = line.price_subtotal - (
                line.purchase_price * line.product_uom_qty)
            line.update({
                'margin': tmp_margin,
                'margin_percent': (tmp_margin / line.price_subtotal * 100.0 if
                                   line.price_subtotal else 0.0),
            })

    def _get_purchase_price(self):
        # Overwrite this function if you don't want to base your
        # purchase price on the product standard_price
        self.ensure_one()
        return self.product_id.standard_price

    @api.onchange('product_id', 'product_uom')
    def _onchange_product_id_repair_margin(self):
        purchase_price = self._get_purchase_price()
        if self.product_uom != self.product_id.uom_id:
            purchase_price = self.product_id.uom_id._compute_price(
                purchase_price, self.product_uom)
        self.purchase_price = purchase_price
