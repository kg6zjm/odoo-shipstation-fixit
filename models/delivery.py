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
from odoo import api, fields, models, _

class delivery_carrier(models.Model):
    _inherit = "delivery.carrier"
   
    shipstation_code = fields.Char('ShipStation Code', size=150)
    
delivery_carrier()

class stock_picking(models.Model):
    _inherit = "stock.picking"
    tracking_ref_ids = fields.One2many('ship.tracking.reference','pick_id','Tracking')
    
stock_picking()

class ship_tracking_reference(models.Model):
    _name = "ship.tracking.reference"
    
    pick_id = fields.Many2one('stock.picking', 'Delivery')
    tracking_code = fields.Char('Tracking Ref',size=150)
    notes = fields.Text('Notes',size=300 )
    status = fields.Selection([('shipping','Shipped'),('voided','Voided'),('return','Returned')],'Status')
    ship_date = fields.Date('Ship Date')
    carr_id = fields.Many2one('delivery.carrier','Carrier')
    service_id=fields.Char('Service Code')
    package_code= fields.Char('Package Code')
    weight= fields.Float('Weight')
    weight_uom= fields.Char('Unit of Measurement')
    dim_unit= fields.Char('Units')
    dim_length=fields.Float('Length')
    dim_width= fields.Float('Width')
    dim_height=fields.Float('Height') 
    sale_id = fields.Many2one('sale.order','Sale')
    shipstation_order_id = fields.Char(
        'ShipStation Order ID',
        readonly=True,
    )
    
    @api.one
    def open_carrier(self):
        count = 0
        li = []
        dic = {}
        ref_obj = self.env['ship.tracking.reference']
        track_obj = self
        url_link=''
        print("track_obj-=====",track_obj)
#                count = count + 1
#                if count < len(track_obj)+1:
#                    dic.update({'date':tr_data.ship_date,'ref':tr_data.tracking_code})
#                    li.append(dic)
#                max_date = max(li, key=lambda x:x['date']) #
        if str(track_obj.carr_id.name).lower().find('usps') != -1:
            url_link = 'https://tools.usps.com/go/TrackConfirmAction.action?tRef=fullpage&tLc=1&text28777=&tLabels='+track_obj.tracking_code
        elif str(track_obj.carr_id.name).lower().find('fedex') != -1:
           url_link = 'https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber='+track_obj.ship_date+track_obj.tracking_code
        elif str(track_obj.carr_id.name).lower().find('ups') != -1:
            url_link = 'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums='+track_obj.tracking_code
        elif url_link:
            return {
                    'type' : 'ir.actions.act_url',
                    'url'  : url_link,
                    'target': 'self'
    
    
                }
ship_tracking_reference()