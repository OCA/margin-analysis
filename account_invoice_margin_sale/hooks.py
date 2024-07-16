def post_init_hook(cr, registry):
    # update purchase_price for invoices from sale_order
    cr.execute(
        """
        UPDATE account_move_line AS aml
        SET
            purchase_price = sol.purchase_price,
            margin = sol.margin,
            margin_signed = CASE
                WHEN am.move_type = 'out_refund' THEN sol.margin * -1
                ELSE sol.margin
            END,
            margin_percent = sol.margin_percent * 100
        FROM sale_order_line sol, account_move am, sale_order_line_invoice_rel rel
        WHERE am.id = aml.move_id
            AND rel.order_line_id = sol.id
            AND rel.invoice_line_id = aml.id;
        """
    )
    # recalculate margin for invoices from sale_order
    cr.execute(
        """
        UPDATE account_move AS am
        SET
            margin = aml.sum_margin,
            margin_signed = aml.sum_margin_signed,
            margin_percent = aml.sum_margin / am.amount_untaxed * 100
        FROM (
            SELECT
                aml.move_id,
                SUM(aml.margin) AS sum_margin,
                SUM(aml.margin_signed) AS sum_margin_signed
            FROM account_move_line AS aml
            GROUP BY aml.move_id
        ) AS aml
        WHERE am.id = aml.move_id
        AND am.amount_untaxed > 0.0;
        """
    )
