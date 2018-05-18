 # -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
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
from openerp import api, fields, models, _
from datetime import date,datetime
from urllib.request import urlopen
import base64
import json
class export_orders_ship(models.Model):
    _name = 'export.orders.ship'

    def export_orders_ship(self):
        context = self._context or {}
        sale_ids = self.env['sale.order'].browse(context.get('active_ids'))
        for so in sale_ids:
            if so.picking_ids:
                if so.picking_ids.state == 'partially_available' or 'assigned':
                    so.shipstation_create_order()