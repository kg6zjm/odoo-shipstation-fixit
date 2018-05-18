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
from odoo.exceptions import Warning
from datetime import date,datetime
from urllib.request import urlopen, Request 
from urllib import error 
import urllib.parse
import base64
import urllib
import encodings
from bs4 import BeautifulSoup
import json
import time
import binascii

class ship_station_config(models.Model):
    _name = 'ship.station.config'
    
    def call_api(self, url, key, value, start_date, page):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url +'shipments?'+ "shipDateStart=" + start_date + "&page=" + str(page) + "&pageSize=500"
        request =Request(url, headers=headers)
        response_body = urlopen(request).read()
        print('response_body====',response_body)
        return json.loads(response_body.decode('utf-8'))
    
    def call_api2(self, url, key, value, orderdate, page):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
    
        url = url+"orders?orderDateStart="+ orderdate + "&page=" + str(page) + "&pageSize=500"
        request = Request(url, headers=headers)
        response_body = urlopen(request).read()
#         response_body=binascii.b2a_base64(str(b64decode(response_body)))
        return json.loads(response_body.decode('utf-8'))

    def get_carrier_api(self,url,key,value):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
    
        url = url+"carriers"
        request=Request(url,headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))
    
    def get_services_api(self,url,key,value,carrierCode):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url+"carriers/listservices?carrierCode="+ carrierCode
        request=Request(url,headers=headers)
        print("request===",type(request))
        response_body=urlopen(request).read()
        print("response_body===",response_body)
        return json.loads(response_body.decode('utf-8'))
    
    def get_tags_api(self,url,key,value):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url+"accounts/listtags"
        print("url1===",type(url))
        request=Request(url,headers=headers)
        response_body=urlopen(request).read()
        print("response_body===",response_body)
        return json.loads(response_body.decode('utf-8'))
    
    def mark_shipped(self,url,key,value,data):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string,    
            'Content-Type':'application/json'
        }
        url = url+"orders/markasshipped"
        print("url=====",url)
        data = data.encode(encoding='UTF-8')
        request=Request(url,data=data,headers=headers)
        try:
            response_body = (urlopen(request).read())
            return json.loads(response_body.decode('utf-8'))
        except error.HTTPError as e:
            error_detail = json.loads(e.read().decode('utf-8'))
            error_message = e.msg + " " + str(e.code) \
                            + "\nError Message: " \
                            + error_detail['Message']
            raise Warning(error_message)
    def create_shipment_label(self,url, key,value,data):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        
        headers = {
            'Authorization': "Basic " + base64string,    
            'Content-Type':'application/json'
        }

        url = url+"shipments/createlabel"
        data = data.encode(encoding='UTF-8')
        request=Request(url,data=data,headers=headers)
        try:
            response_body = urlopen(request).read()
            return json.loads(response_body.decode('utf-8'))
        except error.HTTPError  as e:
            error_detail = json.loads(e.read().decode('utf-8'))
            error_message = e.msg + " " + str(e.code)\
                            + "\nError Message: "\
                            + error_detail['Message']
            raise Warning(error_message)

    def create_sales_order(self, url, key, value, data):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')

        headers = {
            'Authorization': "Basic " + base64string,
            'Content-Type': 'application/json'
        }
        url = url + "orders/createorder"
        data = data.encode(encoding='UTF-8')
        request = Request(url,data=data, headers=headers)
        try:
            response_body = urlopen(request).read()
            return json.loads(response_body.decode('utf-8'))
        except error.HTTPError as e:
            error_detail = json.loads(e.read().decode('utf-8'))
            error_message = e.msg + " " + str(e.code) \
                            + "\nError Message: " \
                            + error_detail['Message']
            raise Warning(error_message)

    def cancel_sales_order(self, url, key, value, order_id):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')

        headers = {
            'Authorization': "Basic " + base64string,
            'Content-Type': 'application/json'
        }

        url = url + "orders/"+ order_id
        request = Request(url, headers=headers)
        request.get_method = lambda: 'DELETE'
        try:
            response_body = urlopen(request).read()
            return json.loads(response_body.decode('utf-8'))
        except HTTPError as e:
            error_detail = json.loads(e.read())
            error_message = e.msg + " " + str(e.code) \
                            + "\nError Message: " \
                            + error_detail['Message']
            raise Warning(error_message)

    def order_create_shipment_label(self, url, key, value, data):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')

        headers = {
            'Authorization': "Basic " + base64string,
            'Content-Type': 'application/json'
        }

        url = url + "orders/createlabelfororder"
        print( "======url====>",url)
        data = data.encode(encoding='UTF-8')
        request = Request(url, data=data, headers=headers)
        print("request=====",request)
        try:
            response_body = urlopen(request).read()
            print("response===",response_body)
            return json.loads(response_body.decode('utf-8'))
        except error.HTTPError as e:
            error_detail = json.loads(e.read().decode('utf-8'))
            error_message = e.msg + " " + str(e.code)\
                            + "\nError Message: "\
                            + error_detail['ExceptionMessage']
            raise Warning(error_message)
    
    def get_rates_api(self,url,key,value,data):
        print("data===for===rate===api====",data)
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        
        headers = {
            'Authorization': "Basic " + base64string,    
            'Content-Type':'application/json'
        }
        url = url+"shipments/getrates"
#         date = data.encode(encoding='UTF-8')
        data = data.encode(encoding='UTF-8')
        request = Request(url,data=data, headers=headers)
        response_body=urlopen(request).read()
        print("response_body=====",response_body)
        return json.loads(response_body.decode('utf-8'))
    
    def get_packages_api(self,url,key,value,carrierCode):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers={
                 'Authorization':'Basic'+ base64string
                 }
        request = Request(url+'carriers/listpackages?carrierCode='+carrierCode,headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))
    
    def get_orders_api(self,url,key,value,createDateStart=False,page=False):
        page=1
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url+"orders?orderDateStart="+ createDateStart + "&page=" + str(page) + "&pageSize=500"
        request = Request(url, headers=headers)
        response_body=urlopen(request).read()
        res= json.loads(response_body.decode('utf-8'))
        print('res==============',res)
        return res
    
    def get_orders_wid_paramtr_api(self,url,key,value,createDateStart=False,store_id=False,page=False):
        page=1
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url+"orders?storeId="+ store_id +"&orderDateStart="+ createDateStart +"&page=" + str(page) + "&pageSize=500"
        request = Request(url, headers=headers)
        response_body=urlopen(request).read()
        res= json.loads(response_body.decode('utf-8'))
        return res

    def get_products_api(self,url,key,value,product_id=False):
        print('get_products_api====',product_id)
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers={
                 'Authorization':"Basic "+ base64string
                 }
        
        if not product_id:
            url = url+'products'
            request = Request(url,headers=headers)
        else:
            url = url+'products/%d'%(product_id)
            request = Request(url,headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))  

    def get_stores_api(self,url,key,value,marketplaceId):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers={
                 'Authorization':"Basic "+ base64string
                 }
        url = url+'stores?marketplaceId='+marketplaceId
        request = Request(url,headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))  

    def get_marketplace_api(self,url,key,value):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        print("base64string=====",base64string)
        headers={
                 'Authorization':"Basic "+ base64string
                 }
        
        url = url+'stores/marketplaces'
        request = Request(url,headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8')) 

    def get_users_api(self,url,key,value):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers={
                 'Authorization':'Basic'+ base64string
                 }
        request = Request(url+'users?showInactive=false',headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))  
    
    def get_customers_api(self,url,key,value):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers={
                 'Authorization':'Basic'+ base64string
                 }
        request = Request(url+'customers',headers=headers)
        response_body=urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))  
    
    def get_order_items(self):
        
        sale_obj = self.env['sale.order']
        cnt = 1
        for record in self:
            try:
                response2 = self.call_api2(record.url, record.user, record.password, record.from_date, cnt)
            except Exception as e:
                pass
            if response2:
                for orders in response2['orders']:
                    sale_id = sale_obj.search([('order_number','=',orders['orderNumber'])])
                    if sale_id:
                        sale_id.write({'customer_notes':str(orders['customerNotes'])})
                if response2['pages']:
                    for i in range(2, response2['pages'] + 1):
                        cnt = cnt + 1
                        try:
                            response2 = self.call_api2(record.url, record.user, record.password, record.from_date, cnt)
                        except e:
                            pass
                        if response2:
                            for orders in response2['orders']:
                                sale_id = sale_obj.search([('order_number','=',orders['orderNumber'])])
                                if sale_id:
                                    sale_id.write({'customer_notes':str(orders['customerNotes'])})
        self._cr.commit()
        return True
    

    
    @api.one
    def get_stores(self):
        print('get_stores========')
        store_obj=self.env['shipstation.stores']
        res=store_obj.create_store()    
        return res
    
    @api.one
    def get_marketplace(self):
        marketplc_obj=self.env['marketplace.shipstatin']
        res=marketplc_obj.create_marketplace() 
        return res
    
    @api.multi
    def write(self,values):
        res=super(ship_station_config,self).write(values)
        if values.get('allow_multiple_label'):
            stock_ids=self.env['stock.picking'].search([('label_done','=',True)])
            for stock in stock_ids:
                stock.write({'label_done':False})
        return res
    
    name=fields.Char('Name')
    url = fields.Char('URL', size=4000)
    user = fields.Char('User', size=600)
    password = fields.Char('Password', size=600)
    from_date = fields.Date('From Date')
    carr_id=fields.Many2one('shipstatn.carrier','Carrier Name')
    allow_multiple_label=fields.Boolean("Allow Label Creation Multiple Times")
    export_order_create = fields.Boolean("Export Order at Creation")
    from_shipment_date = fields.Integer('No of days to get shipment')
    
ship_station_config()
