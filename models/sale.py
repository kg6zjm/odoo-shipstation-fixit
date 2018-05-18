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
class sale_order(models.Model):
    _inherit = 'sale.order'

    ship_date = fields.Date('Shipped Date')
    track_ref = fields.Char('Tracking Reference',size=100)
    customer_notes = fields.Text('Customer Notes',size=400,readonly=True)
    track_sale_ref_ids = fields.One2many('ship.tracking.reference','sale_id','Tracking')
    ship_cost= fields.Char('Ship Cost')
    order_id=fields.Char('Order ID')
    order_number=fields.Char('Order Number')
    order_date=fields.Datetime('Order Date')
    create_date=fields.Datetime('Create Date')
    modify_date=fields.Datetime('Modify Date')
    payment_date=fields.Datetime('Payment Date')
    shipby_date=fields.Datetime('ShipBy Date')
    order_status=fields.Char('Order Status')
#     customerNotes=fields.Char('Customer Notes')
    internal_notes=fields.Char('Internal Notes')
    gift=fields.Boolean('Gift')
    gift_message=fields.Char('Gift Message')
    req_shipping=fields.Char('Requested ShippingService')
    carrier_code=fields.Many2one('shipstatn.carrier','Carrier Code')
    service_code=fields.Many2one('shipstation.services','Service Code')
    package_code=fields.Char('Package Code')
    marketplc_id=fields.Many2one('marketplace.shipstatin','Marketplace')
#     ship_date=fields.Datetime('Ship Date')
    weight=fields.Integer('Weight')
    weight_uom=fields.Many2one('product.uom','Weight UOM')
    dimension_len=fields.Integer('Length')
    dimension_width=fields.Integer('Width')
    dimension_hieght=fields.Integer('Height')
    dimension_unit=fields.Many2one('product.uom','Unit')
    is_shipstation=fields.Boolean('Is shipstation')
    store_id=fields.Many2one('shipstation.stores','Store_id')
    export_order_ids = fields.One2many('export.shipment.order', 'sale_id', string="Export Order Ids")
#     unique_sales_rec_no = fields.Char('Shipstation Order No.',size=400,readonly=True)

    @api.one
    def call_api(self, url, key, value, recp_name, order_num, page):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        print('base64string======',base64string)
        headers = {
            'Authorization': "Basic " + base64string    
        }
        print( headers)
        url = url +"shipments?recipientName="+recp_name +"&orderNumber=" + order_num + "&page=" + str(page) + "&pageSize=500"
        request = Request(url, headers=headers)
        response_body = urlopen(request).read()
        return json.loads(response_body.decode('utf-8'))

    @api.one
    def call_api2(self, url, key, value, orderId, page):
        base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
        headers = {
            'Authorization': "Basic " + base64string    
        }
        url = url+"orders?"+"orderNumber="+ orderId + "&page=" + str(page) + "&pageSize=500"
        request = Request(url, headers=headers)
        response_body = urlopen(request).read()
    
    @api.one
    def get_orders(self):
        self.env.context={}
        cnt = 1
        sale_obj = self.env['sale.order']
        picking_obj = self.env['stock.picking']
#         transfer_wiz_obj = self.env['stock.transfer.details']
        carrier_obj = self.env['delivery.carrier']
        track_obj = self.env['ship.tracking.reference']
        product_object = self.env['product.product']
        partner_object = self.env['res.partner']
        ship_obj = self.env['ship.station.config']
        ship_ids = ship_obj.search([])
        for record in ship_ids:
            try:
                try:
                    sale_data = self
                    if sale_data.partner_id:
                        name = sale_data.partner_id.name
                        index = str(name).find(' ')
                        recp_name = name[:index]
                    response = self.call_api(record.url, record.user, record.password, recp_name, sale_data.amazon_order_id, cnt)
                    response2 = self.call_api2(record.url, record.user, record.password, sale_data.amazon_order_id, cnt)
                except Exception as e:
                    pass
                if response:
                    for order in response['shipments']:
                        sale_ids = sale_obj.search([('amazon_order_id','=', order['orderNumber'])]) #will change for different module
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
                                        part_ids = partner_object.search([('name','=','Shipping and Service')])
                                        if part_ids:
                                            partner_id = part_ids[0]
                                        else:
                                            partner_id = partner_object.create({'name': 'Shipping and Service'})
                                        name = order['serviceCode'].replace('_',' ').upper()
                                        c_id = carrier_obj.create( {'shipstation_code': order['serviceCode'], 'name': name, 'product_id': p_id, 'partner_id': partner_id})
                                track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])
                                status = False
                                if order['isReturnLabel']:
                                    status = 'return'
                                if not order['isReturnLabel'] and not order['voided']:
                                    status = 'shipping'
                                if order['voided']:
                                    status = 'voided'
                                if not track_ids:
                                    tr_id = track_obj.create({'sale_id':sale_id.id,'carr_id':c_id.id,'ship_date':order['shipDate'],'status':status,'tracking_code':order.get('trackingNumber',False)})
                                else:
                                    track_ids.write({'status':status})
                                for order_note in response2['orders']:
                                    sale_ids = sale_obj.search([('amazon_order_id','=', order_note['orderNumber'])])
                                    if sale_ids:
                                        for sale_id in sale_ids:
                                            sale_id.write({'customer_notes':str(order_note['customerNotes'])})

                    if response['pages']:
                        for i in range(2, response['pages'] + 1):
                            cnt = cnt + 1
                            try:
                                sale_data = self
                                response = self.call_api(record.url, record.user, record.password, sale_data.amazon_order_id, cnt)
                                response2 = self.call_api2(record.url, record.user, record.password, sale_data.amazon_order_id, cnt)
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
                                                    c_id = carrier_obj.create( {'shipstation_code': order['serviceCode'], 'name': name, 'product_id': p_id.id, 'partner_id': partner_id.id})
                                            track_ids = track_obj.search([('ship_date','=',order['shipDate']),('tracking_code','=',order.get('trackingNumber',False)),('sale_id','=',sale_id.id)])
                                            status = False
                                            if order['isReturnLabel']:
                                                status = 'return'
                                            if not order['isReturnLabel'] and not order['voided']:
                                                status = 'shipping'
                                            if order['voided']:
                                                status = 'voided'
                                            if not track_ids:
                                                tr_id = track_obj.create({'sale_id':sale_id.id,'carr_id':c_id.id,'ship_date':order['shipDate'],'status':status,'tracking_code':order.get('trackingNumber',False)})
                                            else:
                                                track_ids.write({'status':status})
                for order_note in response2['orders']:
                    sale_ids = sale_obj.search([('amazon_order_id','=', order_note['orderNumber'])])
                    if sale_ids:
                        for sale_id in sale_ids:
                            sale_id.write({'customer_notes':str(order_note['customerNotes'])})
            except Exception as e:
                pass       

#     @api.one
    def create_order_shipstation(self,store_id=False):
        sale_obj=self.env['sale.order']
        sale_line_obj=self.env['sale.order.line']
        product_obj=self.env['product.product']
        partner_obj=self.env['res.partner']
        pricelist_obj=self.env['product.pricelist']
        shipstatn_api=self.env['ship.station.config']
        ship_ids = shipstatn_api.search([('id','=',1)])
        if not store_id: 
            response_vals=shipstatn_api.get_orders_api(ship_ids.url,ship_ids.user,ship_ids.password,ship_ids.from_date)
        else:
            response_vals=shipstatn_api.get_orders_wid_paramtr_api(ship_ids.url,ship_ids.user,ship_ids.password,ship_ids.from_date,store_id)
        if store_id:
            stores_id=self.env['shipstation.stores'].search([('store_id','=',store_id)])[0]
        for order in response_vals.get('orders'):
#             pricelist=pricelist_obj.search[()]
            if order.get('orderTotal'):
                order_vals={
                    'order_id':order.get('orderId'),
                    'order_number':order.get('orderNumber'),
                    'order_key':order.get('orderKey'),
                    'order_date':order.get('orderDate'),
                    'create_date':order.get('createDate'),
                    'modify_date':order.get('modifyDate'),
                    'payment_date':order.get('paymentDate'),
                    'shipby_date':order.get('shipByDate'),
                    'order_status':order.get('orderStatus'),
                    'customer_notes':order.get('customerNotes'),
                    'internalNotes':order.get('internalNotes'),
                    'name':order.get('orderNumber'),
                    'is_shipstation':True,
#                     'carrier_code':order.get('carrierCode'),
#                     'service_code':order.get('serviceCode'),
                    'ship_date':order.get('shipDate'),
                    'shipstation_order_id':order.get('orderId'),
                    }
                if stores_id:
                    order_vals.update({'store_id':stores_id.id,'marketplc_id':stores_id.marketplace_id.id})
                if order.get('carrierCode'):
                    carr_id=self.env['shipstatn.carrier'].search([('code','=',order.get('carrierCode'))])
                    if not carr_id:
                        self.env['shipstatn.carrier'].create({'name':order.get('carrierCode'),'code':order.get('carrierCode')})
                    
                    order_vals.update({'carrier_code':carr_id.id})
                
                if order.get('serviceCode'):
                    service_id=self.env['shipstation.services'].search([('code','=',order.get('serviceCode'))])
                    if not service_id:
                        self.env['shipstation.services'].create({'name':order.get('carrierCode'),'code':order.get('carrierCode'),'carrier_code':carr_id.id})
                    
                    order_vals.update({'service_code':service_id.id})
                
                dimension=order.get('dimensions')
                prodt_uom_id=self.env['product.uom'].search([('name','=','inch(es)')])[0].id
                if  dimension:
                    order_vals.update({
                                       'dim_len':int(dimension.get('length')),
                                       'dim_width':int(dimension.get('width')),
                                       'dim_hieght':int(dimension.get('height')),
                                       'dim_unit':prodt_uom_id
                                       
                                      }) 
                    print("order_vals===",order_vals)  
                weight=order.get('weight')
                product_uom_id=self.env['product.uom'].search([('name','=','oz(s)')])[0].id
                if weight:
                    order_vals.update({'weight_ship':weight.get('value'),
                                       'weight_uom':product_uom_id
                                       
                                       })
    #             customer_vals={
    #                           'customer_id':order.get('customerId'),
    #                           'customer_user_name':order.get('customerUsername'),
    #                           'email':order.get('customerEmail'),
    #                           'name':order.get('billTo').get('name'),
    #                           }
    #             partner_id=partner_obj.search([('customer_id','=',order.get('customerId'))])
    #             print partner_id
    #             if partner_id:
    #                 partner_obj.write(partner_id,customer_vals)
    #             else:
    #                 partner_obj.create(customer_vals)
    #                 err
    #             order_vals.update({'partner_id':partner_id.id})
                
                bill_data=order.get('billTo')
                invoice_addr={
                             'name':bill_data.get('name'),
                             'street':bill_data.get('street1'),
                             'street2':bill_data.get('street2'),
                             'city':bill_data.get('city'),
                             'zip':bill_data.get('postalCode'),
                             'phone':bill_data.get('phone'),
                             'customer_id':order.get('customerId'),
                             'customer_user_name':order.get('customerUsername'),
                             'email':order.get('customerEmail'),
                             'is_shipstation':True,
                             'property_account_receivable_id': 1,
                             'property_account_payable_id': 1
                             }
                country_id=self.env['res.country'].search([('code','=',bill_data.get('country'))])
                if country_id:
                    invoice_addr.update({'country_id':country_id.id})
                state_id=self.env['res.country.state'].search([('name','=',bill_data.get('state'))])
                if state_id:
                    invoice_addr.update({'state_id':state_id.id})
                partner_inv_id=partner_obj.search([('zip','=',bill_data.get('postalCode')),
                                                          ('email','=',order.get('customerEmail'))])
                if not partner_inv_id:
                    invoice_addr_id=partner_obj.create(invoice_addr)
                else:
                    invoice_addr_id=partner_inv_id[0]
                order_vals.update({'partner_invoice_id':invoice_addr_id.id})
                
                ship_data=order.get('shipTo')
                ship_addr={
                          'name':ship_data.get('name'),
                         'street':ship_data.get('street1'),
                         'street2':ship_data.get('street2'),
                         'city':ship_data.get('city'),
                         'zip':ship_data.get('postalCode'),
                         'phone':ship_data.get('phone'),
                         'customer_id':order.get('customerId'),
                         'customer_user_name':order.get('customerUsername'),
                         'email':order.get('customerEmail'),
                         'is_shipstation':True,
                         'property_account_receivable_id':1,
                         'property_account_payable_id':1
                          }
                country_id=self.env['res.country'].search([('code','=',ship_data.get('country'))])
                if country_id:
                    ship_addr.update({'country_id':country_id.id})
                state_id=self.env['res.country.state'].search([('name','=',ship_data.get('state'))])
                if state_id:
                    ship_addr.update({'state_id':state_id.id})
                
                partner_ship_id=partner_obj.search([('zip','=',bill_data.get('postalCode')),
                              ('email','=',order.get('customerEmail'))])
                if not partner_ship_id:
                    ship_addr_id=partner_obj.create(ship_addr)
                else:
                    ship_addr_id=partner_ship_id[0]
                order_vals.update({'partner_shipping_id':ship_addr_id.id})
                order_vals.update({'partner_id':ship_addr_id.id})
                sale_id=sale_obj.search([('order_id','=',order.get('orderId'))])
                if sale_id:
                    sale_id.write(order_vals)
                    sale_id=sale_id.id
                else:
                    sale_id=sale_obj.create(order_vals).id
                
                orderline_items=order.get('items')
                print("orderline_items====",orderline_items)
                for order_line in orderline_items:
    
                    product_id=product_obj.search([('default_code','=',order_line.get('sku'))]).id
                    if not product_id:
                        product_id=product_obj.create_product(order_line.get('productId')).id
                    orderline_vals={
                         'order_item_id':str(order_line.get('orderItemId')),
                         'product_id':product_id,
                         'product_uom':1,
                         'name':order_line.get('name'),
                         'product_uom_qty':order_line.get('quantity'),
                         'price_unit':order_line.get('unitPrice'),
                         'order_id':sale_id,
                        }
                    print("orderline_vals=====",orderline_vals)
                    if order.get('taxAmount'):
                        taxes_id=self.createAccountTax(order.get('taxAmount'), order_line.get('unitPrice'), order_line.get('quantity'))
                        print("tax_id=======",taxes_id)
                        orderline_vals.update({'tax_id':[(6,0,[taxes_id])]})
                        print("jjjjjjjjjjjjjjjjjj========",orderline_vals)
                    sale_line_id=sale_line_obj.search([('order_item_id','=',order_line.get('orderItemId')),('order_id','=',sale_id)])
                    print("sale_line_id====",sale_line_id)
                    if not sale_line_id:
                        sale_line_obj.create(orderline_vals)
                
                # product_id=product_obj.search([('name','=','Shipping and Handling')])[0]
                if order.get('shippingAmount'):
                    prod_ids = product_obj.search([('name', '=', 'Shipping and Handling')])
                    if prod_ids:
                        product_id = prod_ids[0]
                    else:
                        product_id = product_obj.create(
                            {'name': 'Shipping and Handling', 'type': "service", 'categ_id': 1})
                    shipline=order.get('shippingAmount')
                    if shipline:
                        shipline_vals={
                          'name':'Shipping and Handling',
                         'product_id':product_id.id,
                         'product_uom': 1,
                         'description':order_line.get('Shipping and Handling'),
                         'product_uom_qty':1,
                         'price_unit':order.get('shippingAmount'),
                         'order_id':sale_id,
                        }
                        sale_line_id = sale_line_obj.search([('name', '=', 'Shipping and Handling')])
                    if not sale_line_id:
                        sale_line_obj.create(shipline_vals)     
                sale_obj.write({'amount_total':order.get('orderTotal')})
                sale_order_obj=sale_obj.browse(sale_id)
                account_invoice=self.env['account.invoice']
                picking_obj=self.env['stock.picking']
                if sale_order_obj.state in ('draft','sent') : 
                    sale_order_obj.action_confirm()

                    #zubair 04.01.2018...update the stock picking shipment_order_id
                    if sale_order_obj.picking_ids:
                        for pic in sale_order_obj.picking_ids:
                            pic.shipstation_order_id = order.get('orderId')
                            #Create a rescord in the export shipment order one2many table
                            shipment_order_id = self.env['export.shipment.order'].create({'do_id': pic.id, 'shipstation_id': order.get('orderId'), 'sale_id': sale_order_obj.id})

                    shiplineid = False
                    if not sale_order_obj.invoice_ids:
                        shiplineid = sale_order_obj.action_invoice_create()
                    else:
                        shiplineid = sale_order_obj.invoice_ids[0].id
                    # inv_obj = account_invoice.browse(shiplineid[0])
                    shiplineid = self.env['account.invoice'].browse(shiplineid)
                    if shiplineid.state == 'draft':
                        val_id = shiplineid.action_invoice_open()
                    self._cr.commit()
                    invoice_ids = account_invoice.search([('origin','=',sale_order_obj.name)])[0].id
                    acc_obj=account_invoice.browse(invoice_ids)


                            
                if sale_line_id and sale_order_obj.state not in ('done','cancel'):
                    picking_ids = sale_order_obj.picking_ids
                    if picking_ids:
                        if order.get('orderStatus',False) == 'shipped':
                            picking_ids = sale_obj.browse(sale_id).picking_ids
                            for each_picking in picking_ids:
                                each_picking.action_confirm()
                                each_picking.force_assign()
                                each_picking.action_done()
                            sale_order_obj.write({'shipped':True})
    
                        if  order.get('orderStatus',False) not in ('awaiting_payment','awaiting_shipment','cancelled'):
                            invoice_ids = account_invoice.search([('origin','=',sale_order_obj.name)])[0].id
                            acc_obj=account_invoice.browse(invoice_ids)
                            if order.get('orderStatus',False) not in ('awaiting_payment','awaiting_shipment','cancelled'):
                                if acc_obj.state not in ('paid'):
                                    acc_obj.invoice_pay_customer_base()
                                    sale_order_obj.action_done()
                                    sale_order_obj.write({'invoiced':True})
                                    self._cr.commit()
    
    
                if order.get('OrderStatus',False)=='cancelled':
                    if sale_order_obj.state in ('sale','done'):
                        sale_obj.action_cancel(sale_id) 
                        picking_ids = sale_obj.browse(sale_id).picking_ids
                        if picking_ids:
                            for each_picking in picking_ids:
                                picking_id=picking_obj.browse([each_picking.id])
                                if picking_id.state not in ('done'):
                                    picking_id.action_cancel()
                                else:
                                    return_obj=self.env['stock.return.picking']
                                    self._context.update({'active_id':picking_id.id})
                                    res=return_obj.default_get(['product_return_moves','move_dest_exists','original_location_id','parent_location_id','location_id'])
                                    return_id=return_obj.create(res,context=None)
                                    pick_id_return=return_obj.create_returns(return_id,)
                                    picking_obj.force_assign([pick_id_return['res_id']])
                                    picking_obj.action_done([pick_id_return['res_id']])
                                    self._cr.commit()
                    else:
                        sale_obj.action_cancel(sale_id) 
                    if sale_order_obj.state != 'cancel':
                        invoice_ids = account_invoice.search([('origin','=',sale_order_obj.name)])
                        acc_obj=account_invoice.browse(invoice_ids[0]) 
                        if acc_obj:
                            self._context.update({'active_ids':[acc_obj.id]})
                            if acc_obj.state == 'paid':
                                resid=self.env['account.invoice.refund'].create()
                                refund_obj=self.env['account.invoice.refund'].browse(resid)
                                inv_refund_id=refund_obj.invoice_refund()
                                refund_id=inv_refund_id['domain'][1][2][0]
                                val_id=account_invoice.browse(refund_id).signal_workflow('invoice_open')  
                                acc_obj_new=account_invoice.browse(val_id.keys()[0])
                                acc_obj_new.invoice_pay_customer_base()
                                self._cr.commit()
                            else:
                                acc_obj.action_cancel()   
        ship_ids.write({'from_date':date.today()})         
            
                
        return True
    def createAccountTax(self, value, unitprice, quantity):
        accounttax_obj = self.env['account.tax']
        value = ((value * 100.00) / (unitprice * quantity))
        nm = 'Tax(' + str(value) + '%)'
        accounttax_ids = accounttax_obj.search([('name', '=', nm)])
        accounttax_id = ''
        if accounttax_ids:
            accounttax_id = accounttax_ids.id

        else:
            vals = {'price_include': False, 
                    'name': 'Tax(' + str(value) + '%)', 
                    'amount': value,
                    'type_tax_use': 'sale'}
            accounttax_id = accounttax_obj.create(vals).id
        return accounttax_id
        
#    def open_carrier(self, cr, uid, ids, context):
#        count = 0
#        li = []
#        dic = {}
#        ref_obj = self.pool.get('ship.tracking.reference')
#        track_obj = self.browse(cr, uid ,ids).track_sale_ref_ids
#        if len(track_obj):
#            for tr_data in track_obj:
##                count = count + 1
##                if count < len(track_obj)+1:
##                    dic.update({'date':tr_data.ship_date,'ref':tr_data.tracking_code})
##                    li.append(dic)
##                print( "==================",li
##                max_date = max(li, key=lambda x:x['date']) #
##                print( "max_date---------",max_date
#                if str(tr_data.carr_id.name).lower().find('usps') != -1:
#                    url_link = 'https://tools.usps.com/go/TrackConfirmAction.action?tRef=fullpage&tLc=1&text28777=&tLabels='+tr_data.tracking_code
#                elif str(tr_data.carr_id.name).lower().find('fedex') != -1:
#                    url_link = 'https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber='+max_date['ref']+tr_data.tracking_code
#                elif str(tr_data.carr_id.name).lower().find('ups') != -1:
#                    url_link = 'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums='+tr_data.tracking_code
#        
#        return {
#                'type' : 'ir.actions.act_url',
#                'url'  : url_link,
#                'target': 'new'
#    
#    
#                }

    
sale_order()     

class sale_order_line(models.Model):
    _inherit ='sale.order.line'
    order_item_id=fields.Char('Order Item ID')
    exported_on_shipstation = fields.Boolean('Exported on shipstation')
    
    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals=super(sale_order_line,self)._prepare_order_line_procurement(group_id=group_id)                    
        vals.update({
    #       'notes':self.order_id.notes,
    #       'status':self.order_id.order_status,
            'ship_date':self.order_id.ship_date,
            'carr_id' :self.order_id.carrier_code.id,
            'service_id':self.order_id.service_code.id,
            'package_code':self.order_id.package_code,
            'weight_ship':self.order_id.weight,
            'weight_uom':self.order_id.weight_uom.id,
            'dim_unit':self.order_id.dimension_unit.id,
            'dim_length':self.order_id.dimension_len,
            'dim_width':self.order_id.dimension_width,
            'dim_height':self.order_id.dimension_hieght ,
            'is_shipstation':True,
        })
        return vals
    
    
    @api.multi
    def write(self, vals):
        print ("sakle oprder line===============",self,vals)
        #print (errrrrrrrrrrrr)
        res=super(sale_order_line, self).write(vals)
        return res

class account_invoice(models.Model):
    _inherit = "account.invoice"

    def invoice_pay_customer_base(self):
#         self._context={}
#         accountinvoice_link = self.browse()
#         print'accountinvoice_link',accountinvoice_link
#         currentTime = time.strftime("%Y-%m-%d")
        journal_id = self._default_journal()
#       journal = self.pool.get('account.journal').browse(cr,uid,journal_id.id)
#        acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
        if self.browse().type == 'out_invoice':
            self._context['type'] = 'out_invoice'
        elif self.browse().type == 'out_refund':    
            self._context['type'] = 'out_refund'
        self.pay_and_reconcile(journal_id,self.amount_total, False, False)
        return True
account_invoice()

class StockMove(models.Model):
    _inherit = 'stock.move'

    notes = fields.Text('Notes',size=300 )
    status = fields.Selection([('shipping','Shipped'),('voided','Voided'),('return','Returned')],'Status')
    ship_date = fields.Date('Ship Date')
    carr_id = fields.Many2one('shipstatn.carrier','Carrier Code')
    service_id=fields.Many2one('shipstation.services','Service Code')
    package_code= fields.Char('Package Code')
    weight_ship= fields.Float('Weight')
    weight_uom= fields.Many2one('product.uom','Unit of Measurement')
    dim_unit= fields.Many2one('product.uom','Units')
    dim_length=fields.Float('Length')
    dim_width= fields.Float('Width')
    dim_height=fields.Float('Height')  
    is_shipstation=fields.Boolean('Is shipstation')

StockMove()

class ExportShipmentOrder(models.Model):
    _name = 'export.shipment.order'
    
    do_id = fields.Many2one('stock.picking', string="DO")
    shipstation_id = fields.Char(string="Shipstation ID")
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    
    
    
