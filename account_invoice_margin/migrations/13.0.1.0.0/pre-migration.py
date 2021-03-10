# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(env.cr, "ALTER TABLE account_move ADD margin numeric")
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_move ADD margin_signed numeric"
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_move ADD margin_percent numeric"
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_move am
        SET margin = ai.margin,
            margin_signed = ai.margin_signed,
            margin_percent = ai.margin_percent
        FROM account_invoice ai
            WHERE ai.id = am.old_invoice_id""",
    )
    openupgrade.logged_query(env.cr, "ALTER TABLE account_move_line ADD margin numeric")
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_move_line ADD margin_signed numeric"
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_move_line ADD margin_percent numeric"
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_move_line ADD purchase_price numeric"
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE account_move_line aml
        SET margin = ail.margin,
            margin_signed = ail.margin_signed,
            margin_percent = ail.margin_percent,
            purchase_price = ail.purchase_price
        FROM account_invoice_line ail
            WHERE ail.id = aml.old_invoice_line_id""",
    )
