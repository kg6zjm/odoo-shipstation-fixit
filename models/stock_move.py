# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        so_rec = self.env['sale.order'].search(
            [('procurement_group_id', '=', self.group_id.id)])[0]
        order_id = False
        if so_rec and so_rec.shipstation_order_id:
            order_id = so_rec.shipstation_order_id
        vals.update({
            'shipstation_order_id': order_id,
        })
        return vals
