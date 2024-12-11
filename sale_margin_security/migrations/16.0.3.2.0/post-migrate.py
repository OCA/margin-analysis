# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    users_read = env["res.users"].search(
        [("groups_id", "in", env.ref("product_cost_security.group_product_cost").ids)]
    )
    users_read.groups_id += env.ref("sale_margin_security.group_sale_margin_security")

    users_edit = env["res.users"].search(
        [
            (
                "groups_id",
                "in",
                env.ref("product_cost_security.group_product_edit_cost").ids,
            )
        ]
    )
    users_edit.groups_id += env.ref(
        "sale_margin_security.group_sale_margin_edit_security"
    )
