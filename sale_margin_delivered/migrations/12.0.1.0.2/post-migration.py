# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.logged_query(
        cr, """UPDATE sale_order_line
               SET margin_delivered=0,
                   margin_delivered_percent=0,
                   purchase_price_delivery=0
               WHERE qty_delivered = 0 AND margin_delivered > 0
        """)
