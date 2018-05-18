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
from datetime import date,datetime
from urllib.request import urlopen
import base64
import json
import time
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    customer_id= fields.Char('Customer ID')
    customer_user_name=fields.Char('Customer Username')
    is_shipstation=fields.Boolean('Is shipstation')

class marketplace_shipstatin(models.Model):
    _name='marketplace.shipstatin'
    
    name=fields.Char('Name')
    marketplace_id= fields.Char('Marketplace ID')
    can_refresh=fields.Boolean('Can Referesh')
    suprt_cstm_mapins=fields.Boolean('Supports Custom Mappings')
    suprt_cstm_status=fields.Boolean('Supports Custom Statuses')
    can_confrm_shipmnt=fields.Boolean('Can Confirm Shipments')
    
    
    def create_marketplace(self):
        marketplc_obj=self.env['marketplace.shipstatin']
        shipstn_config=self.env['ship.station.config']
        
        shipstatn_api=shipstn_config.search([('id','=',1)])
        print("shipstatn_api====",shipstatn_api)
        shipstatn_response=shipstatn_api.get_marketplace_api(shipstatn_api.url, shipstatn_api.user, shipstatn_api.password)
        for marketplc_data in shipstatn_response:
            marketplace_vals={
                    "name": marketplc_data.get('name'),
                    "marketplace_id": marketplc_data.get('marketplaceId'),
                    "can_refresh": marketplc_data.get('canRefresh'),
                    "suprt_cstm_mapins": marketplc_data.get('supportsCustomMappings'),
                    "suprt_cstm_status": marketplc_data.get('supportsCustomStatuses'),
                    "can_confrm_shipmnt": marketplc_data.get('canConfirmShipments')
                  }
            marketplace_id=marketplc_obj.search([('marketplace_id','=',marketplc_data.get('marketplaceId'))])
            if not marketplace_id:
                marketplc_obj.create(marketplace_vals)
            else:
                marketplace_id.write(marketplace_vals)
        return True        
    
class shipstation_stores(models.Model):
    
    _name='shipstation.stores'
    
    name= fields.Char('Name')
    marketplace_id=fields.Many2one('marketplace.shipstatin','Marketplace')
    store_id = fields.Char('Store')
    email=fields.Char('Email')
    integration_url=fields.Char('Integration Url')
    active =fields.Boolean('Active')
    company_name=fields.Char('Company Name')
    phone=fields.Char('Phone')
    website=fields.Char('Website')


    def create_store(self):
        print('stores===')
        shipstn_config=self.env['ship.station.config']
        shipstation_store=self.env['shipstation.stores']
        marketplc_ids=self.env['marketplace.shipstatin'].search([])
        shipstatn_api=shipstn_config.search([('id','=',1)])
        for marketplace_data in marketplc_ids:
            if marketplace_data.marketplace_id:
                shipstatn_response=shipstatn_api.get_stores_api(shipstatn_api.url, shipstatn_api.user, shipstatn_api.password,marketplace_data.marketplace_id)
                for store_data in shipstatn_response:
                    # marketplace_id = self.env['marketplace.shipstatin'].search(
                    #     [('marketplace_id', '=', store_data.get('marketplaceId'))])
                    store_vals={
                        "store_id": store_data.get('storeId'),
                        "name": store_data.get('storeName'),
                        "marketplace_id": marketplace_data.id,
                        "marketplaceName": store_data.get('marketplaceName'),
                        "email": store_data.get('email'),
                        "integration_url": store_data.get('integrationUrl'),
                        "active": store_data.get('active'),
                        "company_name": store_data.get('companyName'),
                        "phone": store_data.get('phone'),
                        "website": store_data.get('website'),
                      }
                    store_id=shipstation_store.search([('store_id','=',store_data.get('storeId'))])
                    if not store_id:
                        shipstation_store.create(store_vals)
                    else:
                        store_id.write(store_vals)
        return True

    @api.one
    def get_orders(self):
        self.env.context={}
        cnt = 1
#        lis = []
        self.env['ship.station.config'].get_order_items()
        sale_obj = self.env['sale.order']
        stock_picking_obj = self.env['stock.picking']
#         transfer_wiz_obj = self.env['stock.transfer_details']
        carrier_obj = self.env['delivery.carrier']
        track_obj = self.env['ship.tracking.reference']
        product_object = self.env['product.product']
        partner_object = self.env['res.partner']
        response = ''
        recd = self.env['ship.station.config'].search([])
        for record in sale_obj.search([('store_id','=',self.id)]):

            # recd = self.env['ship.station.config'].browse(recd_ids[0])
            try:
                response = recd.call_api(recd.url, recd.user, recd.password, recd.from_date, cnt)
            except Exception as e:
                pass
            if response:
                for order in response['shipments']:
                    # change code...search delivery order and then search sale order and do the process
                    picking_ids = stock_picking_obj.search([('shipstation_order_id','=',order['orderId'])])
                    if picking_ids:
                        for pick in picking_ids:
                            sale_ids = sale_obj.search([('name','=', pick.origin)])
                            # sale_ids = sale_obj.search([('order_number','=', order['orderNumber'])])
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
                                                p_id  = product_object.create({'name': 'Shipping and Handling', 'type':"service" ,'categ_id': 1,'property_account_income_id':1})
                                            part_ids = partner_object.search( [('name','=','Shipping and Service')])
                                            if part_ids:
                                                partner_id = part_ids[0]
                                            else:
                                                partner_id = partner_object.create({'name': 'Shipping and Service'})
                                            name = order['serviceCode'].replace('_',' ').upper()
                                            c_id = carrier_obj.create( {'shipstation_code': order['serviceCode'], 'name': name, 'product_id': p_id.id, 'partner_id': partner_id.id})

                                    status = False
                                    dim_unit = ''
                                    dim_width = ''
                                    dim_length = ''
                                    dim_height = ''
                                    dim_weight = ''
                                    package_code = ''
                                    ship_cost = 0
                                    insurance_ship = False
                                    insure_value = 0
                                    #fetch shipcost
                                    if order.get('shipmentCost'):
                                        ship_cost = order.get('shipmentCost')
                                    # fetch the shipments details of product
                                    if order.get('dimensions'):
                                        #u'dimensions': {u'units': u'inches', u'width': 10.25, u'length': 14.25, u'height': 2.5}
                                        dim_unit = order.get('dimensions').get('units')
                                        dim_width = order.get('dimensions').get('width')
                                        dim_length = order.get('dimensions').get('length')
                                        dim_height = order.get('dimensions').get('height')
                                    #Fetch weight details of Product
                                    if order.get('weight'):
                                        dim_weight = order.get('weight').get('value')
                                        dim_weight_uom = order.get('weight').get('units')
                                        #u'weight': {u'units': u'ounces', u'WeightUnits': 1, u'value': 23.0}
                                    #Fetch Package Code
                                    if order.get('packageCode'):
                                        package_code = order.get('packageCode')
                                    #Fetch insuranceopetions
                                    if order.get('insuranceOpetions'):
                                        insurance_ship = order.get('insuranceOptions').get('insureShipment')
                                        insure_value = order.get('insuranceOpetions').get('insuredValue')
                                    # u'insuranceOptions': {u'insureShipment': False, u'insuredValue': 0.0, u'provider': None},

                                    # fetch Status
                                    if order['isReturnLabel']:
                                        status = 'return'
                                    if not order['isReturnLabel'] and not order['voided']:
                                        status = 'shipping'
                                    if order['voided']:
                                        status = 'voided'

                                    track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])
                                    status = False
                                    if order['isReturnLabel']:
                                        status = 'return'
                                    if not order['isReturnLabel'] and not order['voided']:
                                        status = 'shipping'
                                    if order['voided']:
                                        status = 'voided'

                                    if not track_ids:
                                        track_ids = track_obj.create({'sale_id':sale_id.id,
                                                                      'carr_id':c_id.id,
                                                                      'ship_date':order['shipDate'],
                                                                      'status':status,
                                                                      'tracking_code':order.get('trackingNumber',False),
                                                                      'weight':dim_weight,
                                                                      'dim_unit':dim_unit,
                                                                      'dim_length':dim_length,
                                                                      'dim_width':dim_width,
                                                                      'dim_height':dim_height,
                                                                      'weight_uom':dim_weight_uom,
                                                                      'package_code':package_code,
                                                                      'shipstation_order_id':order['orderId'],
                                                                      'ship_cost':ship_cost,
                                                                      'pick_id':pick.id,
                                                                      })
                                    else:
                                        track_ids.write({'status':status})

                                    # Now add this shipment details in the stock.picking
                                    pick.carrier_tracking_ref = order.get('trackingNumber','')
                                    pick.ship_date = order['shipDate']
                                    pick.track_status = status
                                    pick.carrier_price = ship_cost
                                    pick.package_code = order['packageCode']
                                    pick.weight_ship = dim_weight
                                    pick.dim_width = dim_width
                                    pick.dim_length = dim_length
                                    pick.dim_height = dim_height
                                    pick.insure_shipment = insurance_ship
                                    pick.insure_value= insure_value

                                    if order['serviceCode']:
                                        #search shipstation_carrier 
                                        shipstatn_carrier_srch = self.env['shipstation.services'].search([('code','=',order['serviceCode'])], limit=1)
                                        if shipstatn_carrier_srch:
                                            pick.service_id = shipstatn_carrier_srch.id
                                            pick.carr_id = shipstatn_carrier_srch.carrier_code.id
                                            #Call onchange to add shipment cost in  sale order line
                                            pick.onchange_create_order_line()  


                if response['pages']:
                    
                    for i in range(2, response['pages'] + 1):
                        cnt = cnt + 1
                        try:
                            response = self.call_api(recd.url, recd.user, recd.password, recd.from_date, i)
                        except Exception as e:
                            pass
                        if response:
                            for order in response['shipments']:
                                # change code...search delivery order and then search sale order and do the process
                                picking_ids = stock_picking_obj.search([('shipstation_order_id','=',order['orderId'])])
                                if picking_ids:
                                    for pick in picking_ids:
                                        sale_ids = sale_obj.search([('name','=', pick.origin)])
                                        # sale_ids = sale_obj.search([('order_number','=', order['orderNumber'])])
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
                                                            p_id  = product_object.create( {'name': 'Shipping and Handling', 'type':"service" ,'categ_id': 1,'property_account_income_id':1})
                                                        part_ids = partner_object.search( [('name','=','Shipping and Service')])
                                                        if part_ids:
                                                            partner_id = part_ids[0]
                                                        else:
                                                            partner_id = partner_object.create( {'name': 'Shipping and Service'})
                                                        name = order['serviceCode'].replace('_',' ').upper()
                                                        c_id = carrier_obj.create( {'shipstation_code': order['serviceCode'], 'name': name, 'product_id': p_id.id, 'partner_id': partner_id.id})
                                                            
                                                status = False
                                                dim_unit = ''
                                                dim_width = ''
                                                dim_length = ''
                                                dim_height = ''
                                                dim_weight = ''
                                                package_code = ''
                                                ship_cost = 0
                                                insurance_ship = False
                                                insure_value = 0
                                                #fetch shipcost
                                                if order.get('shipmentCost'):
                                                    ship_cost = order.get('shipmentCost')
                                                # fetch the shipments details of product
                                                if order.get('dimensions'):
                                                    #u'dimensions': {u'units': u'inches', u'width': 10.25, u'length': 14.25, u'height': 2.5}
                                                    dim_unit = order.get('dimensions').get('units')
                                                    dim_width = order.get('dimensions').get('width')
                                                    dim_length = order.get('dimensions').get('length')
                                                    dim_height = order.get('dimensions').get('height')
                                                #Fetch weight details of Product
                                                if order.get('weight'):
                                                    dim_weight = order.get('weight').get('value')
                                                    dim_weight_uom = order.get('weight').get('units')
                                                    #u'weight': {u'units': u'ounces', u'WeightUnits': 1, u'value': 23.0}
                                                #Fetch Package Code
                                                if order.get('packageCode'):
                                                    package_code = order.get('packageCode')
                                                #Fetch insuranceopetions
                                                if order.get('insuranceOpetions'):
                                                    insurance_ship = order.get('insuranceOptions').get('insureShipment')
                                                    insure_value = order.get('insuranceOpetions').get('insuredValue')
                                                # u'insuranceOptions': {u'insureShipment': False, u'insuredValue': 0.0, u'provider': None},

                                                # fetch Status
                                                if order['isReturnLabel']:
                                                    status = 'return'
                                                if not order['isReturnLabel'] and not order['voided']:
                                                    status = 'shipping'
                                                if order['voided']:
                                                    status = 'voided'

                                                track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])
                                                status = False
                                                if order['isReturnLabel']:
                                                    status = 'return'
                                                if not order['isReturnLabel'] and not order['voided']:
                                                    status = 'shipping'
                                                if order['voided']:
                                                    status = 'voided'

                                                track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])

                                                if not track_ids:
                                                    track_ids = track_obj.create({'sale_id':sale_id.id,
                                                                      'carr_id':c_id.id,
                                                                      'ship_date':order['shipDate'],
                                                                      'status':status,
                                                                      'tracking_code':order.get('trackingNumber',False),
                                                                      'weight':dim_weight,
                                                                      'dim_unit':dim_unit,
                                                                      'dim_length':dim_length,
                                                                      'dim_width':dim_width,
                                                                      'dim_height':dim_height,
                                                                      'weight_uom':dim_weight_uom,
                                                                      'package_code':package_code,
                                                                      'shipstation_order_id':order['orderId'],
                                                                      'ship_cost':ship_cost,
                                                                      'pick_id':pick.id,
                                                                      })
                                                else:
                                                    track_ids.write({'status':status})

                                                # Now add this shipment details in the stock.picking
                                                pick.carrier_tracking_ref = order.get('trackingNumber','')
                                                pick.ship_date = order['shipDate']
                                                pick.track_status = status
                                                pick.carrier_price = ship_cost
                                                pick.package_code = order['packageCode']
                                                pick.weight_ship = dim_weight
                                                pick.dim_width = dim_width
                                                pick.dim_length = dim_length
                                                pick.dim_height = dim_height
                                                pick.insure_shipment = insurance_ship
                                                pick.insure_value= insure_value

                                                if order['serviceCode']:
                                                    #search shipstation_carrier 
                                                    shipstatn_carrier_srch = self.env['shipstation.services'].search([('code','=',order['serviceCode'])], limit=1)
                                                    if shipstatn_carrier_srch:
                                                        pick.service_id = shipstatn_carrier_srch.id
                                                        pick.carr_id = shipstatn_carrier_srch.carrier_code.id
                                                        #Call onchange to add shipment cost in  sale order line
                                                        pick.onchange_create_order_line()  

        recd.write({'from_date':time.strftime("%Y-%m-%d")})
        return True
    
    
    
    
    
    @api.one
    def get_services(self):
        carr_ids=self.env['shipstatn.carrier'].search([('id','>=',1)])
        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        serv_obj=self.env['shipstation.services']
        if carr_ids:
            for carr_id in carr_ids:
                res=serv_obj.create_shipstation_services(ship_ids.url,ship_ids.user,ship_ids.password,carr_id.code)    
        return True
    
    @api.one
    def get_carriers(self):
        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        carr_obj=self.env['shipstatn.carrier']
        res=carr_obj.create_shipstatn_carrier(ship_ids.url,ship_ids.user,ship_ids.password)    
        return res
    
    @api.one
    def create_orders(self):
        store=self.store_id
        sale_obj=self.env['sale.order']
        sale_obj.create_order_shipstation(store)
        return True
    
    @api.one
    def create_tags(self):
        store = self.store_id
        print('store==========',store)
        ship_tags_obj = self.env['shipstation.tags']
        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        serv_obj = self.env['shipstation.services']
        res = ship_tags_obj.create_shipstation_tags(ship_ids.url,ship_ids.user,ship_ids.password)    
        return True
    
class shipstation_carrier(models.Model):
    _name='shipstatn.carrier'
    
    name=fields.Char('Name')
    code = fields.Char('Code')
    account_no=fields.Char('Account Number')
    balance=fields.Char('Balance')
    
    def create_shipstatn_carrier(self,url,user,password):
        carrier_obj=self.env['shipstatn.carrier']
        shipstn_config=self.env['ship.station.config']
        
        shipstatn_api=shipstn_config.search([('id','=',1)])
        shipstatn_response=shipstatn_api.get_carrier_api(url, user, password)
        carrier_id = ''
        print('shipresponse=========',shipstatn_response)
        for carrier_data in shipstatn_response:
            carrier_vals={
                          "name": carrier_data.get('name'),
                          "code": carrier_data.get('code'),
                          "account_no":carrier_data.get('accountNumber'),
                          "balance":carrier_data.get('balance')
                          }
            carrier_id = carrier_obj.search([('code','=',carrier_data.get('code'))])
            if carrier_id:
                carrier_id=carrier_id.write(carrier_vals)
            else:
                carrier_id=carrier_obj.create(carrier_vals)
        return carrier_id
    
class shipstation_services(models.Model):
    
    _name ='shipstation.services'
    
    carrier_code=fields.Many2one('shipstatn.carrier')
    name=fields.Char('Name')
    code = fields.Char('Code')    
    domestic =fields.Boolean('Domestic')
    international =fields.Boolean('International')

    def create_shipstation_services(self,url,user,password,carrierCode):
        service_obj=self.env['shipstation.services']
        shipstn_config=self.env['ship.station.config']
        
        shipstatn_api=shipstn_config.search([('id','=',1)])
        shipstatn_response=shipstatn_api.get_services_api(url,user,password,carrierCode)
        
        carr_id=self.env['shipstatn.carrier'].search([('code','=',carrierCode)])
        service_id = ''
        for service_carrier in shipstatn_response:
            service_vals={
                          "name": service_carrier.get('name'),
                          "carrier_code": carr_id.id,
                          "code":service_carrier.get('code'),
                          "domestic":service_carrier.get('domestic'),
                          "international":service_carrier.get('international')
                          }
            service_id = service_obj.search([('code','=',service_carrier.get('code'))])
            if service_id:
                service_id=service_id.write(service_vals)
            else:
                service_id=service_obj.create(service_vals)
        return service_id

class shipstation_tags(models.Model):
    _name='shipstation.tags'

    name = fields.Char('Name')
    code = fields.Char('Code')
    tag_color = fields.Char('Tag Color')
    # [{u'color': u'#FF0000', u'tagId': 40258, u'name': u'Partial'}]

    def create_shipstation_tags(self,url,user,password):
        shipstn_config = self.env['ship.station.config']
        shipstatn_response = shipstn_config.get_tags_api(url, user, password)
        tag_id = ''
        for tag_data in shipstatn_response:
            tag_vals={
                          "name": tag_data.get('name'),
                          "code": tag_data.get('tagId'),
                          "tag_color":tag_data.get('color'),
                          }
            print("tag_vals====",tag_vals)
            tag_id = self.search([('code','=',tag_data.get('code'))])
            if tag_id:
                tag_id = tag_id.write(tag_vals)
            else:
                tag_id = self.create(tag_vals)
        return tag_id
                    
                    