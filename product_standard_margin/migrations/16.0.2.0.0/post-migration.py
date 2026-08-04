import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    for company in env["res.company"].with_context(active_test=False).search([]):
        products = (
            env["product.product"]
            .with_company(company)
            .search(
                [
                    ("company_id", "=", company.id),
                    ("standard_markup_rate", "=", 999.0),
                    ("standard_price", "!=", 0.0),
                ]
            )
        )
        _logger.info(
            f"Company {company.name}:"
            f" Trying to recomputing margin fields for {len(products)} products ..."
        )
        products._compute_margin()
