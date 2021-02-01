# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    margin = fields.Monetary(
        string="Margin",
        compute="_compute_margin",
        digits="Product Price",
        store=True,
        currency_field="currency_id",
    )

    margin_signed = fields.Monetary(
        string="Margin Signed",
        compute="_compute_margin",
        digits="Product Price",
        store=True,
        currency_field="currency_id",
    )

    margin_percent = fields.Float(
        string="Margin (%)",
        digits="Product Price",
        compute="_compute_margin",
        store=True,
    )

    def _get_margin_applicable_lines(self):
        self.ensure_one()
        return self.invoice_line_ids

    @api.depends(
        "invoice_line_ids.margin",
        "invoice_line_ids.margin_signed",
        "invoice_line_ids.price_subtotal",
    )
    def _compute_margin(self):
        for invoice in self:
            margin = 0.0
            margin_signed = 0.0
            price_subtotal = 0.0
            for line in invoice._get_margin_applicable_lines():
                margin += line.margin
                margin_signed += line.margin_signed
                price_subtotal += line.price_subtotal
            invoice.margin = margin
            invoice.margin_signed = margin_signed
            invoice.margin_percent = (
                price_subtotal and margin_signed / price_subtotal * 100 or 0.0
            )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    margin = fields.Float(
        compute="_compute_margin", digits="Product Price", store=True, string="Margin"
    )
    margin_signed = fields.Float(
        compute="_compute_margin",
        digits="Product Price",
        store=True,
        string="Margin Signed",
    )
    margin_percent = fields.Float(
        string="Margin (%)", compute="_compute_margin", store=True, readonly=True
    )
    purchase_price = fields.Float(
        string="Cost",
        compute="_compute_purchase_price",
        store=True,
        readonly=False,
        digits="Product Price",
    )

    @api.depends("purchase_price", "price_subtotal")
    def _compute_margin(self):
        for line in self:
            if line.move_id and line.move_id.type[:2] == "in":
                line.update(
                    {"margin": 0.0, "margin_signed": 0.0, "margin_percent": 0.0}
                )
                continue
            tmp_margin = line.price_subtotal - (line.purchase_price * line.quantity)
            sign = line.move_id.type in ["in_refund", "out_refund"] and -1 or 1
            line.update(
                {
                    "margin": tmp_margin,
                    "margin_signed": tmp_margin * sign,
                    "margin_percent": (
                        tmp_margin / line.price_subtotal * 100.0
                        if line.price_subtotal
                        else 0.0
                    ),
                }
            )

    def _get_purchase_price(self):
        # Overwrite this function if you don't want to base your
        # purchase price on the product standard_price
        self.ensure_one()
        return self.product_id.standard_price

    @api.depends("product_id", "product_uom_id")
    def _compute_purchase_price(self):
        for line in self:
            if line.move_id.type in ["out_invoice", "out_refund"]:
                purchase_price = line._get_purchase_price()
                if line.product_uom_id != line.product_id.uom_id:
                    purchase_price = line.product_id.uom_id._compute_price(
                        purchase_price, line.product_uom_id
                    )
                line.purchase_price = purchase_price
            else:
                line.purchase_price = 0.0
