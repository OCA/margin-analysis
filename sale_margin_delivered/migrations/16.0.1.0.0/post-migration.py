# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    sale_margin_delivered_security = env["ir.module.module"].search(
        [
            ("name", "=", "sale_margin_delivered_security"),
            ("state", "=", "uninstalled"),
        ]
    )
    if sale_margin_delivered_security:
        sale_margin_delivered_security.state = "to install"
