import logging

from odoo.tools import column_exists, create_column

_logger = logging.getLogger(__name__)

COLUMNS = (
    ("account_invoice", "margin"),
    ("account_invoice", "margin_signed"),
    ("account_invoice", "margin_percent"),
    ("account_invoice_line", "margin"),
    ("account_invoice_line", "margin_signed"),
    ("account_invoice_line", "margin_percent"),
    ("account_invoice_line", "purchase_price"),
)


def pre_init_hook(cr):
    for table, column in COLUMNS:
        if not column_exists(cr, table, column):
            _logger.info("Create column %s in database", column)
            create_column(cr, table, column, "numeric")
    cr.execute(
        """
        WITH ai AS(
            SELECT id FROM account_invoice WHERE type NOT ILIKE 'in_%'
        )
        UPDATE account_invoice_line
            SET margin = price_subtotal, margin_signed = price_subtotal,
                margin_percent = 100
        FROM ai
        WHERE ai.id = account_invoice_line.invoice_id
        AND price_subtotal > 0.0;
    """
    )
    cr.execute(
        """
        WITH ail AS(
            SELECT
               account_invoice_line.invoice_id,
               SUM(account_invoice_line.margin) AS sum_margin,
               SUM(account_invoice_line.margin_signed) AS sum_margin_signed
            FROM account_invoice_line
            INNER JOIN account_invoice
            ON account_invoice.id = account_invoice_line.invoice_id
            GROUP BY account_invoice_line.invoice_id
        )
        UPDATE account_invoice
            SET margin = ail.sum_margin,
                margin_signed = ail.sum_margin_signed,
                margin_percent = ail.sum_margin_signed / amount_untaxed * 100
        FROM ail
        WHERE account_invoice.id = ail.invoice_id
        AND account_invoice.amount_untaxed > 0.0
    """
    )
