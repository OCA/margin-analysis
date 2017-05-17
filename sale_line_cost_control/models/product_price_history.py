# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'
    # if we have more than one entry at the same time
    # we want to get the last created
    _order = 'datetime desc, id desc'
