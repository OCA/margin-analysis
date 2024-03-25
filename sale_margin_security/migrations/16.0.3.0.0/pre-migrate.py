# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    old = env.ref("sale_margin_security.group_sale_margin_security")
    new = env.ref("product_cost_security.group_product_edit_cost")
    cr.execute(
        """
            INSERT INTO res_groups_users_rel (gid, uid)
            SELECT %s, uid FROM res_groups_users_rel WHERE gid = %s
            ON CONFLICT DO NOTHING
        """,
        (new.id, old.id),
    )
