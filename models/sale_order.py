# -*- coding: utf-8 -*-
# Copyright 2017 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, http, _
from datetime import date,datetime
from urllib.request import urlopen
import base64
import json
import logging
logger = logging.getLogger('sale_order')

class SaleOrder(models.Model):
    _inherit = "sale.order"

    shipstation_order_id = fields.Char(
        'ShipStation Order ID',
         readonly=True,copy=False
    )

#     @api.multi
#     def action_confirm(self):
#         res = super(SaleOrder, self.with_context({'from_sale': True})).action_confirm()
#         for record in self:
#             if not record.invoice_ids:
#                 inv_id = record.action_invoice_create()
#         return res
    # @api.multi
    # def write(self, vals):
    #     config = self.env['ship.station.config']
    #     ship_config_ids = config.search([])
    #     print 'ship_config_ids============',ship_config_ids,ship_config_ids.export_order_create
    #     # ship_config =  self.env['ship.station.config'].browse(ship_config_ids[0])
    #
    #     for order in self:
    #         if 'state' in vals:
    #             if self.invoice_ids:
    #                 for inv in self.invoice_ids:
    #                     if inv.state == 'paid':
    #                 # if vals['state'] == 'sale':
    #                         if ship_config_ids.export_order_create:
    #                             order.shipstation_create_order()
    #             if vals['state'] == 'cancel' and order.shipstation_order_id:
    #                 order.shipstation_delete_order()
    #     res = super(SaleOrder, self).write(vals)
    #     return res

    @api.one
    def shipstation_create_order(self):
        print("========",self.picking_ids)
        item_list = []
        base_url = http.request.env['ir.config_parameter'].get_param(
            'web.base.url')
        for picking in self.picking_ids:
            for line in picking.pack_operation_product_ids:
                for l_so in self.order_line:
                    bom = self.env['mrp.bom']._bom_find(product=l_so.product_id, picking_type=picking.picking_type_id, company_id=picking.company_id.id)
                    if bom:
                        for bom_line in bom.bom_line_ids:
                            if bom_line.product_id.id == line.product_id.id:
                                product_image = base_url + "/website/image/product.template/" \
                                        + str(bom_line.product_id.product_tmpl_id.id) + "/image"
                                item_list.append({
                                    "sku": "%s" % (bom_line.product_id.default_code),
                                    "name": "%s" % (bom_line.product_id.name),
                                    "imageUrl": "%s" % (product_image),
                                    "quantity": int(bom_line.product_qty) * int(l_so.product_qty),
                                    "unitPrice": 0.0,
                                    "taxAmount": 0.0
                                })
                    else:
                        product = line.product_id
                        product_image = base_url + "/website/image/product.template/" \
                                        + str(line.product_id.product_tmpl_id.id) + "/image"
                        if l_so.product_id == product:
                            item_list.append({
                                "sku": "%s" % (product.code),
                                "name": "%s" % (product.name),
                                "imageUrl": "%s" % (product_image),
                                "quantity": int(line.product_qty),
                                "unitPrice": l_so.price_unit,
                                "taxAmount": l_so.tax_id.amount
                            })
                        

        items_json = json.dumps(item_list)

        values = """{
            "orderNumber": "%s",
            "orderDate": "%s",
            "orderStatus": "awaiting_shipment",
            "customerUsername": "%s",
            "customerEmail": "%s",
            "billTo": {
                "name": "%s",
                "street1": "%s",
                "street2": "%s",
                "city": "%s",
                "state": "%s",
                "postalCode": "%s",
                "country": "%s",
                "phone": "%s"
            },
		    "shipTo": {
                "name": "%s",
                "street1": "%s",
                "street2": "%s",
                "city": "%s",
                "state": "%s",
                "postalCode": "%s",
                "country": "%s",
                "phone": "%s"
            },
            "items": %s,
            "amountPaid": %f,
            "taxAmount": %f,
            "shippingAmount": %f
        }
    """ % (
			self.name,
			self.date_order,
			self.partner_id.name,
			self.partner_id.email,
			self.partner_invoice_id.name,
			self.partner_invoice_id.street,
			self.partner_invoice_id.street2 or "",
			self.partner_invoice_id.city,
			self.partner_invoice_id.state_id.code,
			self.partner_invoice_id.zip,
			self.partner_invoice_id.country_id.code,
			self.partner_invoice_id.phone,
			self.partner_shipping_id.name,
			self.partner_shipping_id.street,
			self.partner_shipping_id.street2 or "",
			self.partner_shipping_id.city,
			self.partner_shipping_id.state_id.code,
			self.partner_shipping_id.zip,
			self.partner_shipping_id.country_id.code,
            self.partner_shipping_id.phone,
			items_json,
			self.amount_total,
			self.amount_tax,
			self.amount_delivery,
			
        )
       
        ship_ids = self.env['ship.station.config'].search([('id', '=', 1)])
        res = self.env['ship.station.config'].create_sales_order(
            ship_ids.url, ship_ids.user, ship_ids.password, values)
        order_id = res.get('orderId')
        self.write({'shipstation_order_id': order_id})
        
        
    @api.one
    def shipstation_create_order(self):
        item_list = []
        delivery_order_ids = self.env['stock.picking']
        print("delivery_order_ids===",delivery_order_ids)
        base_url = http.request.env['ir.config_parameter'].get_param(
            'web.base.url')
        for picking in self.picking_ids:
            if picking.state == 'done':
                continue
            amount_total = 0.0
            amount_untax_total = 0.0
            print("self.order_line====",self.order_line)
            for l_so in self.order_line:
                print("exported_on_shipstation====",l_so.exported_on_shipstation)
                if l_so.exported_on_shipstation:
                    continue
                if l_so.product_id.bom_ids:
                    item_list.append({
                        "sku": l_so.product_id and l_so.product_id.default_code or '',
                        "name": 'KIT',
                        "imageUrl": '',
                        "quantity": int(l_so.product_qty),
                        "unitPrice": l_so.price_unit,
                        "taxAmount": 0.0
                    })
                    print("item_list",item_list)
                    amount_total += l_so.price_unit
                    tax = 0
                    for tax_l in l_so.tax_id:
                        tax += tax_l.amount
                    amount_untax_total += l_so.price_unit * tax/100
                    l_so.write({'exported_on_shipstation': True})
                    for bom_line in l_so.product_id.bom_ids[0].bom_line_ids:
                        product_image = base_url + "/website/image/product.template/" \
                                + str(bom_line.product_id.product_tmpl_id.id) + "/image"
                        item_list.append({
                            "sku": "%s" % (bom_line.product_id.default_code),
                            "name": "    - %s" % (bom_line.product_id.name),
                            "imageUrl": "%s" % (product_image),
                            "quantity": int(bom_line.product_qty) * int(l_so.product_qty),
                            "unitPrice": 0.0,
                            "taxAmount": 0.0
                        })
                else:
                    product = l_so.product_id
                    product_image = base_url + "/website/image/product.template/" \
                                    + str(l_so.product_id.product_tmpl_id.id) + "/image"
                    amount_total += l_so.price_unit
                    tax = 0
                    for tax_l in l_so.tax_id:
                        tax += tax_l.amount
                    amount_untax_total += l_so.price_unit * tax/100
                    l_so.write({'exported_on_shipstation': True})
                    if l_so.product_id == product:
                        item_list.append({
                            "sku": "%s" % (product.code),
                            "name": "%s" % (product.name),
                            "imageUrl": "%s" % (product_image),
                            "quantity": int(l_so.product_qty),
                            "unitPrice": l_so.price_unit,
                            "taxAmount": l_so.tax_id.amount
                        })
            if item_list:
                items_json = json.dumps(item_list)
        
                values = """{
                    "orderNumber": "%s",
                    "orderDate": "%s",
                    "orderStatus": "awaiting_shipment",
                    "customerUsername": "%s",
                    "customerEmail": "%s",
                    "billTo": {
                        "name": "%s",
                        "street1": "%s",
                        "street2": "%s",
                        "city": "%s",
                        "state": "%s",
                        "postalCode": "%s",
                        "country": "%s",
                        "phone": "%s"
                    },
                    "shipTo": {
                        "name": "%s",
                        "street1": "%s",
                        "street2": "%s",
                        "city": "%s",
                        "state": "%s",
                        "postalCode": "%s",
                        "country": "%s",
                        "phone": "%s"
                    },
                    "items": %s,
                    "amountPaid": %f,
                    "taxAmount": %f,
                    "shippingAmount": %f
                }
            """ % (
                    self.name,
                    self.date_order,
                    self.partner_id.name,
                    self.partner_id.email,
                    self.partner_invoice_id.name,
                    self.partner_invoice_id.street,
                    self.partner_invoice_id.street2 or "",
                    self.partner_invoice_id.city,
                    self.partner_invoice_id.state_id.code,
                    self.partner_invoice_id.zip,
                    self.partner_invoice_id.country_id.code,
                    self.partner_invoice_id.phone,
                    self.partner_shipping_id.name,
                    self.partner_shipping_id.street,
                    self.partner_shipping_id.street2 or "",
                    self.partner_shipping_id.city,
                    self.partner_shipping_id.state_id.code,
                    self.partner_shipping_id.zip,
                    self.partner_shipping_id.country_id.code,
                    self.partner_shipping_id.phone,
                    items_json,
                    amount_total + amount_untax_total,
                    round(amount_total),
                    self.amount_delivery,
                    
                ) 
                print("values= of=saleorder=======",values)
                ship_ids = self.env['ship.station.config'].search([('id', '=', 1)])

                res = self.env['ship.station.config'].create_sales_order(
                    ship_ids.url, ship_ids.user, ship_ids.password, values)
                order_id = res.get('orderId')
    #             picking.write({'shipstation_order_id': order_id})
                self.write({'shipstation_order_id': order_id})
                delivery_order_ids.write({'shipstation_order_id': order_id})
                picking.shipstation_order_id = order_id     #update the picking shipstation order id
                print("==created==>",self.env['export.shipment.order'].create({'do_id': picking.id, 'shipstation_id': order_id, 'sale_id': self[0].id}))
    

    @api.one
    def shipstation_create_parti_order(self):
        print("partial---------------------")
        item_list = []
        base_url = http.request.env['ir.config_parameter'].get_param(
            'web.base.url')
        
        for picking in self.picking_ids:
            
            if picking.state == 'done':
                
                continue
            amount_total = 0.0
            amount_untax_total = 0.0
            pack_available_ids = [pack.product_id.id for pack in picking.move_lines]
            for l_so in self.order_line:
#                 if l_so.exported_on_shipstation:
#                     continue
                bom = self.env['mrp.bom']._bom_find(product=l_so.product_id, picking_type=picking.picking_type_id, company_id=picking.company_id.id)
                if bom:
                    in_back_order = []
                    in_back_order_dict = {}
                    b_product_ids = [bomm.product_id.id for bomm in bom.bom_line_ids]
                    print("b_product_ids====",b_product_ids)
                    if picking.backorder_id:
                        for bline in picking.backorder_id.move_lines: 
                            if bline.product_id.id in b_product_ids:
                                if bline.product_id.id not in in_back_order:
                                    in_back_order.append(bline.product_id.id) 
                                    reserve =  bline.reserved_availability - bline.initial_demamd
                                    print("reserve----",reserve)
                                    in_back_order_dict.update({bline.product_id.id :reserve})
                                else:
                                    reserve =  in_back_order_dict.get(bline.product_id.id) + bline.reserved_availability - bline.initial_demamd
                                    in_back_order_dict.update({bline.product_id.id : reserve})
                        for pack_o in picking.move_lines:
                            if pack_o.product_id.id in b_product_ids:
                                if pack_o.product_id.id not in in_back_order:
                                    in_back_order.append(pack_o.product_id.id) 
                                    reserve =  pack_o.reserved_availability - pack_o.initial_demamd
                                    print("reserve====222",reserve)
                                    in_back_order_dict.update({pack_o.product_id.id : reserve})
                                else:
                                    reserve =  in_back_order_dict.get(pack_o.product_id.id) + pack_o.reserved_availability - pack_o.initial_demamd
                                    in_back_order_dict.update({pack_o.product_id.id : reserve})
                    else:
                        for pack_o in picking.move_lines:
                            print("pack_o===",pack_o)
                            if pack_o.product_id.id in b_product_ids:
                                if pack_o.product_id.id not in in_back_order:
                                    in_back_order.append(pack_o.product_id.id) 
                                    reserve =  pack_o.reserved_availability - pack_o.initial_demamd
                                    print("reserve=====3333",reserve)
                                    in_back_order_dict.update({pack_o.product_id.id : reserve})
                                else:
                                    reserve =  in_back_order_dict.get(pack_o.product_id.id) + pack_o.reserved_availability - pack_o.initial_demamd
                                    in_back_order_dict.update({pack_o.product_id.id : reserve})
                    if cmp(b_product_ids, in_back_order) == 0:
                        flag = 1
                        for boml in bom.bom_line_ids:
                            print("boml===",boml)
                            if in_back_order_dict.get(boml.product_id.id):
                                if boml.product_qty != in_back_order_dict.get(boml.product_id.id):
                                    flag = 0
                        if flag != 1:
                            continue
                    else:
                        continue
                    item_list.append({
                        "sku": l_so.product_id and l_so.product_id.default_code or '',
                        "name": 'KIT',
                        "imageUrl": '',
                        "quantity": int(l_so.product_qty),
                        "unitPrice": l_so.price_unit,
                        "taxAmount": 0.0
                    })
                    print("item_list=====1111",item_list)
                    l_so.write({'exported_on_shipstation': True})
#                     m_line = False
#                     for bline in picking.move_lines: 
#                         if l_so.product_id.id == bline.product_id.id:
#                             m_line = bline
#                             break
#                     print( "=m_line=======>",m_line)
                    amount_total += l_so.price_unit
                    tax = 0
                    for tax_l in l_so.tax_id:
                        tax += tax_l.amount
                    amount_untax_total += l_so.price_unit * tax/100
                    for bom_line in l_so.product_id.bom_ids[0].bom_line_ids:
                        product_image = base_url + "/website/image/product.template/" \
                                + str(bom_line.product_id.product_tmpl_id.id) + "/image"
                        item_list.append({
                            "sku": "%s" % (bom_line.product_id.default_code),
                            "name": "    - %s" % (bom_line.product_id.name),
                            "imageUrl": "%s" % (product_image),
                            "quantity": int(bom_line.product_qty) * int(l_so.product_qty),
                            "unitPrice": 0.0,
                            "taxAmount": 0.0
                        })
                        print("item_list=====2222",item_list)
                else:
                    print("lllpack_available_ids===",pack_available_ids)
                    if l_so.product_id.id in pack_available_ids:
                        l_so.write({'exported_on_shipstation': True})
                        m_line = False
                        for bline in picking.move_lines: 
                            if l_so.product_id.id == bline.product_id.id:
                                m_line = bline
                                break
                        print( "=m_line=======>",m_line)
                        amount_total += l_so.price_unit
                        tax = 0
                        for tax_l in l_so.tax_id:
                            tax += tax_l.amount
                        amount_untax_total += l_so.price_unit * tax/100
                        product = l_so.product_id
                        product_image = base_url + "/website/image/product.template/" \
                                        + str(l_so.product_id.product_tmpl_id.id) + "/image"
                        if l_so.product_id == product:
                            reserve =  m_line.reserved_availability - m_line.initial_demamd
#                             m_line.write({'initial_demamd': m_line.initial_demamd+reserve})
                            if reserve > 0:
                                item_list.append({
                                    "sku": "%s" % (product.code),
                                    "name": "%s" % (product.name),
                                    "imageUrl": "%s" % (product_image),
                                    "quantity": int(reserve),
                                    "unitPrice": l_so.price_unit,
                                    "taxAmount": l_so.tax_id.amount
                                })
                                print("====item_list=====>",item_list)
                    

            if item_list:
                items_json = json.dumps(item_list)
                print ("items_jsonitems_json==>",items_json)
                values = """{
                        "orderNumber": "%s",
                        "orderDate": "%s",
                        "orderStatus": "awaiting_shipment",
                        "customerUsername": "%s",
                        "customerEmail": "%s",
                        "billTo": {
                            "name": "%s",
                            "street1": "%s",
                            "street2": "%s",
                            "city": "%s",
                            "state": "%s",
                            "postalCode": "%s",
                            "country": "%s",
                            "phone": "%s"
                        },
                        "shipTo": {
                            "name": "%s",
                            "street1": "%s",
                            "street2": "%s",
                            "city": "%s",
                            "state": "%s",
                            "postalCode": "%s",
                            "country": "%s",
                            "phone": "%s"
                        },
                        "items": %s,
                        "amountPaid": %f,
                        "internalNotes": "Partial Shipments",
                        "tagIds": ["40258"],
                        "taxAmount": %f,
                        "shippingAmount": %f
                    }
                """ % (
                    self.name,
                    self.date_order,
                    self.partner_id.name,
                    self.partner_id.email,
                    self.partner_invoice_id.name,
                    self.partner_invoice_id.street,
                    self.partner_invoice_id.street2 or "",
                    self.partner_invoice_id.city,
                    self.partner_invoice_id.state_id.code,
                    self.partner_invoice_id.zip,
                    self.partner_invoice_id.country_id.code,
                    self.partner_invoice_id.phone,
                    self.partner_shipping_id.name,
                    self.partner_shipping_id.street,
                    self.partner_shipping_id.street2 or "",
                    self.partner_shipping_id.city,
                    self.partner_shipping_id.state_id.code,
                    self.partner_shipping_id.zip,
                    self.partner_shipping_id.country_id.code,
                    self.partner_shipping_id.phone,
                    items_json,
                    amount_total + amount_untax_total,
                    round(amount_total),
                    self.amount_delivery,
        
                )
                ship_ids = self.env['ship.station.config'].search([('id', '=', 1)])
                res = self.env['ship.station.config'].create_sales_order(
                    ship_ids.url, ship_ids.user, ship_ids.password, values)
                order_id = res.get('orderId')
                self.write({'shipstation_order_id': order_id})
                picking.shipstation_order_id = order_id     #update the shipstation order id


    @api.one
    def shipstation_delete_order(self):
        ship_ids = self.env['ship.station.config'].search([('id', '=', 1)])
        self.env['ship.station.config'].cancel_sales_order(
            ship_ids.url, ship_ids.user,
            ship_ids.password, self.shipstation_order_id)
        self.shipstation_order_id = False

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
        self.env.context = {}
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
                # wiz_data = self[0]
                logger.info('record.url ===> %s', record.url)
                logger.info('record.user ===> %s', record.user)
                logger.info('record.password ===> %s', record.password)
                # logger.info('wiz_data.order_date ===> %s', wiz_data.order_date)
                response = self.call_api(record.url, record.user, record.password, ship_ids.from_date, cnt)
                logger.info('response ===> %s', response)
                if response:
                    for order in response['shipments']:
                        # for order in response['shipments']:
                        #     print order
                        sale_ids = sale_obj.search([('name', '=', order.get('orderNumber'))])
                        logger.info('sale_ids ===> %s', sale_ids)
                        if sale_ids:
                            for sale_id in sale_ids:
                                sobj = sale_id
                                c_id = False
                                if order['serviceCode']:
                                    c_ids = carrier_obj.search([('shipstation_code', '=', order['serviceCode'])])
                                    if c_ids:
                                        c_id = c_ids[0]
                                    else:
                                        prod_ids = product_object.search([('name', '=', 'Shipping and Handling')])
                                        if prod_ids:
                                            p_id = prod_ids[0]
                                        else:
                                            p_id = product_object.create(
                                                {'name': 'Shipping and Handling', 'type': "service", 'categ_id': 1})
                                        part_ids = partner_object.search([('name', '=', 'Shipping and Service')])
                                        if part_ids:
                                            partner_id = part_ids[0]
                                        else:
                                            partner_id = partner_object.create({'name': 'Shipping and Service'})
                                        name = order['serviceCode'].replace('_', ' ').upper()
                                        c_id = carrier_obj.create(
                                            {'shipstation_code': order['serviceCode'], 'name': name,
                                             'product_id': p_id.id, 'partner_id': partner_id.id})
                                track_ids = track_obj.search([('ship_date', '=', order['shipDate']), (
                                'tracking_code', '=', order.get('trackingNumber', False)),
                                                              ('sale_id', '=', sale_id.id)])
                                logger.info('track_ids ===> %s', track_ids)
                                if not track_ids:
                                    logger.info('if not track_ids ===>')
                                    tr_id = track_obj.create(
                                        {'sale_id': sale_id.id, 'carr_id': c_id.id, 'ship_date': order['shipDate'],
                                         'tracking_code': order.get('trackingNumber', False)})
                                    for pick_id in sale_ids.picking_ids:
                                            # if pick_id.state == 'partially_available':
                                            #     self.picking_ids._create_backorder()
                                            # if not pick_id.backorder_id:
                                            wiz_act = pick_id.do_transfer()
                                            logger.info('wiz_act ===> %s', wiz_act)

                    if response['pages']:
                        logger.info('pages ===>')
                        for i in range(2, response['pages'] + 1):
                            cnt = cnt + 1
                            try:
                                wiz_data = self
                                response = self.call_api(record.url, record.user, record.password,
                                                         ship_ids.from_date, cnt)
                            except Exception as e:
                                pass
                            logger.info('response ==pages=> %s', response)
                            if response:
                                for order in response['shipments']:
                                    sale_ids = sale_obj.search([('name', '=', order.get('orderNumber'))])
                                    if sale_ids:
                                        for sale_id in sale_ids:
                                            sobj = sale_id
                                            c_id = False
                                            if order['serviceCode']:
                                                c_ids = carrier_obj.search(
                                                    [('shipstation_code', '=', order['serviceCode'])])
                                                if c_ids:
                                                    c_id = c_ids[0]
                                                else:
                                                    prod_ids = product_object.search(
                                                        [('name', '=', 'Shipping and Handling')])
                                                    if prod_ids:
                                                        p_id = prod_ids[0]
                                                    else:
                                                        p_id = product_object.create(
                                                            {'name': 'Shipping and Handling', 'type': "service",
                                                             'categ_id': 1})
                                                    part_ids = partner_object.search(
                                                        [('name', '=', 'Shipping and Service')])
                                                    if part_ids:
                                                        partner_id = part_ids[0]
                                                    else:
                                                        partner_id = partner_object.create(
                                                            {'name': 'Shipping and Service'})
                                                    name = order['serviceCode'].replace('_', ' ').upper()
                                                    c_id = carrier_obj.create(
                                                        {'shipstation_code': order['serviceCode'], 'name': name,
                                                         'product_id': p_id.id, 'partner_id': partner_id.id})
                                            track_ids = track_obj.search([('ship_date', '=', order['shipDate']), (
                                            'tracking_code', '=', order.get('trackingNumber', False)),
                                                                          ('sale_id', '=', sale_id.id)])

                                            logger.info('track_ids ==pages=> %s', track_ids)
                                            if not track_ids:
                                                tr_id = track_obj.create({'sale_id': sale_id.id, 'carr_id': c_id.id,
                                                                          'ship_date': order['shipDate'],
                                                                          'tracking_code': order.get(
                                                                              'trackingNumber', False)})
                                                # sale_ids.write('')
                                                for pick_id in sale_ids.picking_ids:
                                                    # if pick_id.state == 'partially_available':
                                                    #     self.picking_ids._create_backorder()
                                                    # if not pick_id.backorder_id:
                                                    wiz_act = pick_id.do_transfer()
                                                    logger.info('wiz_act ===> %s', wiz_act)
            except Exception as e:
                logger.info('Exception ===> %s', e)
                pass
        return True


    @api.model
    def get_orders_shipments_import(self):
        '''This scheduler will import the sale order and delivey order from the shipstation to odoo.
            and also import the shipment related data in the sale order and delivery order.
        '''
        import_shipped_obj = self.env['import.shipped.orders']
        shipstatn_api = self.env['ship.station.config']
        ship_ids = shipstatn_api.search([])
        stores_ids = self.env['shipstation.stores'].search([])
        today_date = datetime.now().date()
        for ship in ship_ids:
            for store in stores_ids:
                #call store import method
                store.create_orders()
            
            # Import the Shipment related data 
            days_for = ship.from_shipment_date if ship.from_shipment_date else 0
            if days_for:
                days_for = days_for if days_for < 0 else -(days_for)
            date_for_shipment = today_date + timedelta(days=days_for)
            import_ship_id = import_shipped_obj.create({'order_date':date_for_shipment})
            if import_ship_id:
                # call method to import the shipment data
                import_ship_id.get_orders()

        return True

class account_payment(models.Model):
    _inherit = "account.payment"

#     @api.model
#     def create(self, vals):
#         res = super(account_payment, self).create(vals)
#         config = self.env['ship.station.config']
#         ship_config_ids = config.search([])
#         inv_id = self.env['account.invoice'].search([('number','=',vals.get('communication'))])
#         so_id = self.env['sale.order'].search([('name', '=', inv_id.origin)])
        # if res:
        #     # if vals['state'] == 'sale':
        #     if ship_config_ids.export_order_create:
        #         so_id.shipstation_create_order()
        # if vals['state'] == 'cancel' and order.shipstation_order_id:
        #     order.shipstation_delete_order()
# 
#         return res