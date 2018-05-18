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
from odoo import fields, api,models
from openerp.tools.translate import _

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _prepare_picking_assign(self):
        vals=super(StockMove,self)._prepare_picking_assign()
        vals.update({
#           'status':move.status,
            'ship_date':self.ship_date,
            'carr_id' :self.carr_id.id,
            'service_id':self.service_id.id,
            'package_code':self.package_code,
            'weight_ship':self.weight_ship,
            'weight_uom':self.weight_uom.id,
            'dim_unit':self.dim_unit.id,
            'dim_length':self.dim_length,
            'dim_width':self.dim_width,
            'dim_height':self.dim_height,
            'is_shipstation':True,
        })
        return vals    

StockMove()


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        result.update({    
#             'status':procurement.status,
            'ship_date':self.ship_date,
            'carr_id' :self.carr_id.id,
            'service_id':self.service_id.id,
            'package_code':self.package_code,
            'weight_ship':self.weight_ship,
            'weight_uom':self.weight_uom.id,
            'dim_unit':self.dim_unit.id,
            'dim_length':self.dim_length,
            'dim_width':self.dim_width,
            'dim_height':self.dim_height,
            'is_shipstation':True,
        })
        return result
ProcurementRule()

class magento_shop(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def import_track_id(self, cron_mode=True):
        instance_obj = self.env['sale.order']
        instance_id = instance_obj.search([])
        instance_id.get_orders()
        return True
# class ProcurementOrder(models.Model):
#     _inherit = "procurement.order"
# 
#     def _run_move_create(self):
#         vals=super(ProcurementOrder,self)._run_move_create()
#         vals.update({    
# #           'status':procurement.status,
#             'ship_date':self.ship_date,
#             'carr_id' :self.carr_id.id,
#             'service_id':self.service_id.id,
#             'package_code':self.package_code,
#             'weight_ship':self.weight_ship,
#             'weight_uom':self.weight_uom.id,
#             'dim_unit':self.dim_unit.id,
#             'dim_length':self.dim_length,
#             'dim_width':self.dim_width,
#             'dim_height':self.dim_height,
#             'is_shipstation':True,
#         })
#         return vals
#         
# ProcurementOrder()
#     