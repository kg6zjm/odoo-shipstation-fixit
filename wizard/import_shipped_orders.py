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
import urllib3
from urllib.request import urlopen
import base64
import json
import logging
logger = logging.getLogger('import_shipped_orders')

class import_shipped_orders(models.Model):
    _name = 'import.shipped.orders'

    order_date = fields.Date('From date')
    
    def call_api(self, url, key, value, start_date, page):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url + "shipments?shipDateStart=" + start_date + "&page=" + str(page) + "&pageSize=500"
        logger.info('url ===> %s', url)
        request = Request(url, headers=headers)
        response_body = urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))
    
    def get_orders(self):
        self.env.context={}
        cnt = 1
        sale_obj = self.env['sale.order']
#         picking_obj = self.env['stock.picking']
#         transfer_wiz_obj = self.env['stock.transfer_details']
        carrier_obj = self.env['delivery.carrier']
        track_obj = self.env['ship.tracking.reference']
        product_object = self.env['product.product']
        partner_object = self.env['res.partner']
        ship_obj = self.env['ship.station.config']
        ship_ids = ship_obj.search([])
        for record in ship_ids:
            try:
                wiz_data = self[0]
                logger.info('record.url ===> %s', record.url)
                logger.info('record.user ===> %s', record.user)
                logger.info('record.password ===> %s', record.password)
                logger.info('wiz_data.order_date ===> %s', wiz_data.order_date)
                response = self.call_api(record.url, record.user, record.password, wiz_data.order_date, cnt)
                logger.info('response ===> %s', response)
                if response:
                    for order in response['shipments']:
                        sale_ids = sale_obj.search( [('order_id','=', order['orderNumber'])])
                        if sale_ids:
                            for sale_id in sale_ids:
                                sobj = sale_id
                                c_id = False
                                if order['serviceCode']:
                                    c_ids = carrier_obj.search([('shipstation_code','=', order['serviceCode'])])
                                    if c_ids:
                                        c_id = c_ids[0]
                                    else:
                                        prod_ids = product_object.search([('name', '=','Shipping and Handling')])
                                        if prod_ids:
                                            p_id  = prod_ids[0]
                                        else: 
                                            p_id  = product_object.create( {'name': 'Shipping and Handling', 'type':"service" ,'categ_id': 1})
                                        part_ids = partner_object.search( [('name','=','Shipping and Service')])
                                        if part_ids:
                                            partner_id = part_ids[0]
                                        else:
                                            partner_id = partner_object.create( {'name': 'Shipping and Service'})
                                        name = order['serviceCode'].replace('_',' ').upper()
                                        c_id = carrier_obj.create( {'shipstation_code': order['serviceCode'], 'name': name, 'product_id': p_id.id, 'partner_id': partner_id.id})
                                track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])
                                if not track_ids:
                                    tr_id = track_obj.create({'sale_id':sale_id.id,'carr_id':c_id.id,'ship_date':order['shipDate'],'tracking_code':order.get('trackingNumber',False)})
                    
                    if response['pages']:
                        for i in range(2, response['pages'] + 1):
                            cnt = cnt + 1
                            try:
                                wiz_data = self
                                response = self.call_api(record.url, record.user, record.password, wiz_data.order_date, cnt)
                            except Exception as e:
                                pass
                            if response:
                                for order in response['shipments']:
                                    sale_ids = sale_obj.search([('amazon_order_id','=', order['orderNumber'])])
                                    if sale_ids:
                                        for sale_id in sale_ids:
                                            sobj = sale_id
                                            c_id = False
                                            if order['serviceCode']:
                                                c_ids = carrier_obj.search([('shipstation_code','=', order['serviceCode'])])
                                                if c_ids:
                                                    c_id = c_ids[0]
                                                else:
                                                    prod_ids = product_object.search([('name', '=','Shipping and Handling')])
                                                    if prod_ids:
                                                        p_id  = prod_ids[0]
                                                    else: 
                                                        p_id  = product_object.create({'name': 'Shipping and Handling', 'type':"service" ,'categ_id': 1})
                                                    part_ids = partner_object.search([('name','=','Shipping and Service')])
                                                    if part_ids:
                                                        partner_id = part_ids[0]
                                                    else:
                                                        partner_id = partner_object.create({'name': 'Shipping and Service'})
                                                    name = order['serviceCode'].replace('_',' ').upper()
                                                    c_id = carrier_obj.create({'shipstation_code': order['serviceCode'], 'name': name, 'product_id': p_id.id, 'partner_id': partner_id.id})
                                            track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])
                                            if not track_ids:
                                                tr_id = track_obj.create({'sale_id':sale_id.id,'carr_id':c_id.id,'ship_date':order['shipDate'],'tracking_code':order.get('trackingNumber',False)})
                                                # sale_ids.write('')
                                                wiz_act = sale_ids.picking_ids.do_transfer()
            except Exception as e:
                logger.info('Exception ===> %s', e)
                pass                                    
        return True
import_shipped_orders()