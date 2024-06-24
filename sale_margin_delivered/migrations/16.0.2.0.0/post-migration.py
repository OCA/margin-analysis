import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version=None):
    """Store margin delivered precentage as a fraction of 1"""
    cr.execute(
        """
        UPDATE sale_order_line
        SET margin_delivered_percent = margin_delivered_percent / 100
        WHERE margin_delivered_percent > 0
        """
    )
    _logger.info("Updated %d records", cr.rowcount)
