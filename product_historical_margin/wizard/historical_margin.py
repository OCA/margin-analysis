# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime

from openerp.osv.orm import TransientModel
from openerp.osv import fields


class historical_margin(TransientModel):
    _name = 'historical_margin'
    _description = 'Product historical margin'
    _columns = {
        'start_date': fields.date('Start Date', help='Date of the first invoice to take into account. The earliest existing invoice will be used if left empty'),
        'end_date': fields.date('End Date', help='Date of the last invoice to take into account. The latest existing invoice will be used if left empty')
        }
    _defaults = {
        'start_date': lambda *a: datetime.date(datetime.date.today().year, 1, 1),
        #'end_date': lambda *a: datetime.date.today(),
        }

    def historical_margin_open_window(self, cr, uid, ids, context=None):
        """
        Open the historical margin view
        """
        if context is None:
            context = {}
        wiz = self.read(cr, uid, ids, [], context)[0]
        ctx = context.copy()
        ctx['start_date']  = wiz.get('start_date')
        ctx['end_date'] = wiz.get('end_date')
        # XXX FIXME
        
