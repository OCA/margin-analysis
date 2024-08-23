import logging

from odoo.tools import column_exists, create_column

_logger = logging.getLogger(__name__)

COLUMNS = (
    ("account_move", "margin"),
    ("account_move", "margin_signed"),
    ("account_move", "margin_percent"),
    ("account_move_line", "margin"),
    ("account_move_line", "margin_signed"),
    ("account_move_line", "margin_percent"),
    ("account_move_line", "purchase_price"),
)


def pre_init_hook(cr):
    for table, column in COLUMNS:
        if not column_exists(cr, table, column):
            _logger.info("Create column %s in database", column)
            create_column(cr, table, column, "numeric")
    cr.execute(
        """
        WITH am AS(
            SELECT id FROM account_move WHERE move_type NOT ILIKE 'in_%'
        )
        UPDATE account_move_line
            SET margin = price_subtotal, margin_signed = price_subtotal,
                margin_percent = 100
        FROM am
        WHERE am.id = account_move_line.move_id
        AND price_subtotal > 0.0;
    """
    )
    if column_exists(cr, "sale_order_line", "purchase_price"):
        # Copy margins from Sale Orders, if possible
        _logger.info("Copy margins from Sale Orders to Invoices...")
        cr.execute(
            """
            WITH margins AS (
                SELECT aml.id
                 , SUM(sol.purchase_price * sol.product_uom_qty)
                   / SUM(sol.product_uom_qty) as purchase_price_unit
            FROM account_move_line aml
              INNER JOIN account_move am
                      ON aml.move_id = am.id
              INNER JOIN sale_order_line_invoice_rel rel
                      ON rel.invoice_line_id = aml.id
              INNER JOIN sale_order_line sol
                      ON rel.order_line_id = sol.id
            WHERE am.move_type NOT ILIKE 'in_%'
              AND aml.price_subtotal <> 0
              AND sol.product_uom_qty <> 0
              AND sol.purchase_price <> 0
            GROUP BY aml.id
            HAVING SUM(sol.purchase_price) <> 0
            )
            UPDATE account_move_line
               SET purchase_price = m.purchase_price_unit * quantity
                 , margin = price_subtotal - (m.purchase_price_unit * quantity)
                 , margin_signed = price_subtotal - (m.purchase_price_unit * quantity)
                 , margin_percent = (price_subtotal - (m.purchase_price_unit * quantity))
                   / price_subtotal
            FROM margins m
            WHERE m.id = account_move_line.id ;
            """
        )
    cr.execute(
        """
        WITH aml AS(
            SELECT
               account_move_line.move_id,
               SUM(account_move_line.margin) AS sum_margin,
               SUM(account_move_line.margin_signed) AS sum_margin_signed
            FROM account_move_line
            INNER JOIN account_move
            ON account_move.id = account_move_line.move_id
            WHERE account_move_line.exclude_from_invoice_tab = false
            GROUP BY account_move_line.move_id
        )
        UPDATE account_move
            SET margin = aml.sum_margin,
                margin_signed = aml.sum_margin_signed,
                margin_percent = aml.sum_margin_signed / amount_untaxed * 100
        FROM aml
        WHERE account_move.id = aml.move_id
        AND account_move.amount_untaxed > 0.0
    """
    )
