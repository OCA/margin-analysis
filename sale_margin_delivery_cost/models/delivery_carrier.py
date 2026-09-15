# Copyright (C) 2021 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    charge_policy = fields.Selection(
        [
            ("sale", "As SO Line"),
            ("other", "As Other Cost"),
        ],
        string="Charging Policy",
        default="sale",
        required=True,
        help="How shipping costs are added to the sales order:"
        " charged in a sales order line, estimated on an other costs line.",
    )
