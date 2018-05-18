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
import base64
import binascii
from base64 import b64decode
from openerp.exceptions import UserError
from openerp.exceptions import Warning
import logging
logger = logging.getLogger('stock')

class stock_picking(models.Model):
    _inherit='stock.picking'

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
    get_rate_ids=fields.One2many('get.rates.services','stock_id','Rates Info')
    label=fields.Binary('Label')
    is_shipstation=fields.Boolean('Is shipstation')
    label_done=fields.Boolean('Label Done')
    carrier_price = fields.Float("Shipping Cost")
    
    # >>> Quartile Limited
    insurance_provider = fields.Selection(
        [('shipsurance', 'Shipsurance Discount Insurance'),
         ('carrier', 'Carrier Declared Value')],
        default='shipsurance',
        string='Provider',
    )
    insurance_value = fields.Float('Insurance Value')
    insure_shipment = fields.Boolean(
        'Insure Shipment',
        default=False,
    )
    shipstation_order_id = fields.Char(
        'ShipStation Order ID',
        readonly=True,copy=False
    )

    track_status = fields.Selection([('shipping','Shipped'),('voided','Voided'),('return','Returned')],'Status')
    # @api.multi
    # def action_assign(self):
    #     """ Check availability of picking moves.
    #     This has the effect of changing the state and reserve quants on available moves, and may
    #     also impact the state of the picking as it is computed based on move's states.
    #     @return: True
    #     """
    #     self.filtered(lambda picking: picking.state == 'draft').action_confirm()
    #     moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
    #     if not moves:
    #         raise UserError(_('Nothing to check the availability for.'))
    #     moves.action_assign()
    #     print'hghghg=========109rccc=======', self.state
    #     config = self.env['ship.station.config']
    #     ship_config_ids = config.search([])
    #     sale_id = self.env['sale.order'].search([('name','=',self.origin)])
    #     if self.state == 'partially_available':
    #         # self._create_backorder()
    #         if not sale_id.shipstation_order_id:
    #             print 'if state'
    #             if ship_config_ids.export_order_create:
    #                 sale_id.shipstation_create_parti_order()
    #     return True

    # <<< Quartile Limited

    #create shipment cost line in the sale order line
    @api.onchange('carrier_price')
    def onchange_create_order_line(self):
        print("self===",self)
        for rec in self:
            product_id = False
            if rec.origin:
                sale_ids = self.env['sale.order'].search([('name','=', rec.origin)])
                print("sale_ids===",sale_ids)
                if rec.service_id:
                    carrier_id = self.env['delivery.carrier'].search([('shipstation_code','=',rec.service_id.code)], limit=1)
                    print("carrier_id======",carrier_id)
                    product_id = carrier_id.product_id.id if carrier_id else False
                    print("produc=====",product_id)
# if not delivery_carrier                 
                    if not product_id:
                        product_id = self.env['product.product'].create({'name': rec.service_id.name, 'type':'service'})
                        print ("product=======================",product_id)
                        delivery_carrier_id = self.env['delivery.carrier'].create({'name': rec.service_id.name,'shipstation_code':rec.service_id.code,'product_id':product_id.id})
                        print ("delivery ethod=====================",delivery_carrier_id)
                        product_id = product_id.id
                        
                product_ids = self.env['product.product'].search([('id', '=',product_id)], limit=1)
                print("product_ids====",product_ids)
                ship_add = [j for i in sale_ids for j in i.order_line if j.product_id == product_ids]
                print("ship_add=====",ship_add)
                # if no shipping cost line added in the sale order line then create order line
                if len(ship_add) == 0:
                    print ("leeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    #create sale order line and link with this sale order
                    if product_ids:
                        order_line_id = self.env['sale.order.line'].create({'product_id':product_ids.id, 
                                                                        'product_uom_qty': 1, 
                                                                        'order_id': sale_ids.id, 
                                                                        'order_partner_id': sale_ids.partner_id.id,
                                                                        'price_unit': rec.carrier_price,
                                                                        'state': 'sale',
                                                                         })
                        print ("order line ind,o",order_line_id)
                
                else:
                    print ("else")
                    ship_add[0].price_unit = rec.carrier_price
                    

    '''
    @api.one
    def export_to_shipstation(self, state):
        sale_ids = self.env['sale.order'].search([('name', '=', self.origin)])
        if sale_ids:
            flag = 0
            if not sale_ids.export_order_ids:
                flag = 1
            for order in sale_ids.export_order_ids:
                if order.do_id.id != self.id:
                    flag = 1
            if flag == 1:
                if state == 'assigned':
                    sale_ids[0].shipstation_create_order()
                elif state == 'partially_available':
                    sale_ids[0].shipstation_create_parti_order()
        return True
    '''

    # Implemented write method compare to older one. Fixed some technical bugs. - By Jignesh
#     @api.multi
#     def write(self, vals):
#         print("self====",self)
#         res = super(stock_picking, self).write(vals)
#         print("res===",res)
#         for picking in self:
#             print("pikking======state====",picking.state)
#             if not picking.shipstation_order_id and picking.state in ['assigned','confirmed']:
#                 sale_ids = self.env['sale.order'].search([('name', '=', picking.origin)])
#                 print("sale_ids====",sale_ids)
#                 if sale_ids:
#                     # if state in 'assigned' state then call
#                     if picking.state == 'confirmed':
#                         sale_ids.shipstation_create_order()
#                     # if state in 'partially_available' then call 
#                     if picking.state == 'assigned':
#                         sale_ids.shipstation_create_parti_order()
#         return res
    
    @api.model
    def create(self ,vals):
        sale_obj= self.env['sale.order']
        sale_ids = sale_obj.search([('name','=',self.origin)])
        if sale_ids:
            val.update({'is_shipstation': True})
        val = super(stock_picking, self).create(vals)
        return val
    
    
    @api.one
    def export_shipment(self):
        flag=0
        for rec in self.move_lines:
            if rec.product_uom_qty != rec.reserved_availability:
                flag = 1
        sale_ids = self.env['sale.order'].search([('name', '=', self.origin)])
        print("sale_ids=====",sale_ids)
        if sale_ids:
            if flag == 0:
                sale_ids.shipstation_create_order()
            else:
                sale_ids.shipstation_create_parti_order()
    @api.one
    def create_label(self):
        # Quartile Limited: var never use
        #stock_obj=self.env['stock.picking']
        stock_browse=self
        print("stock_browse=====",stock_browse)
        frm_partner=stock_browse.picking_type_id.warehouse_id.partner_id
        to_partner=stock_browse.partner_id
        # Quartile Limited: var never use
        #weight=self.env['sale.order'].search([('name','=',stock_browse.origin)])[0].weight
        
        if not stock_browse.carr_id:
            raise Warning(_('Please Select Carrier '))
        if not stock_browse.service_id:
            raise Warning(_('Please Select Service '))
        if not stock_browse.scheduled_date:
            raise Warning(_('Please set Shipping Date'))
        if not stock_browse.weight_ship:
            raise Warning(_('Please select Weight'))
        if not stock_browse.dim_width:
            raise Warning(_('Please select Dimension Width'))
        if not stock_browse.dim_length :
            raise Warning(_('Please select Dimension Length '))
        if not stock_browse.dim_height :
            raise Warning(_('Please select Dimension Height '))
        if not frm_partner.street:
            raise Warning(_('Please set Street for Company'))
        if not frm_partner.city:
            raise Warning(_('Please set City for Company '))
        if not frm_partner.state_id:
            raise Warning(_('Please set State for Company '))
        if not frm_partner.zip:
            raise Warning(_('Please set Postal Code for Company '))
        if not frm_partner.country_id:
            raise Warning(_('Please set Country for Company '))
        if not frm_partner.phone:
            raise Warning(_('Please set Phone for Company'))    
        if not to_partner.name:
            raise Warning(_('Please set Name for Customer'))
        if not to_partner.street:
            raise Warning(_('Please set Street for Customer '))  
        if not to_partner.city:
            raise Warning(_('Please set City for Customer '))
        if not to_partner.state_id:
            raise Warning(_('Please set State for Customer'))  
        if not to_partner.zip:
            raise Warning(_('Please set Postal code for Customer'))
        if not to_partner.country_id:
            raise Warning(_('Please set Country for Customer'))  
        if not to_partner.phone:
            raise Warning(_('Please set Phone for Customer'))

        # >>> Quartile Limited
        if stock_browse.insure_shipment:
            insurance_opt = """
                "insuranceOptions": {
                    "provider": "%s",
                    "insureShipment": true,
                    "insuredValue": %d
                }
            """ % (
                stock_browse.insurance_provider,
                int(stock_browse.insurance_value)
            )
            print("insurance_opt====",type(insurance_opt))
        else:
            insurance_opt = ""
#             """
#                 "insuranceOptions": null
#             """
        values = """
            {
                "orderId": %s,
                "carrierCode": "%s",
                "serviceCode": "%s",
                "packageCode": "package",
                "confirmation": "delivery",
                "shipDate": "%s",
                "weight": {
                    "value": %d,
                    "units": "%s"
                },
                "dimensions": {
                    "units": "%s",
                    "length": %d,
                    "width": %d,
                    "height": %d
                },
                "shipFrom": {
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
                'testLabel': 'true'
            }
        """ %(
            stock_browse.shipstation_order_id,
            stock_browse.carr_id.code,
            stock_browse.service_id.code,
            stock_browse.scheduled_date and stock_browse.scheduled_date[:10] or '',
            int(stock_browse.weight_ship),
            str(stock_browse.weight_uom.name),
            str(stock_browse.dim_unit.name),
            int(stock_browse.dim_length),
            int(stock_browse.dim_width),
            int(stock_browse.dim_height),
            frm_partner.name,
            frm_partner.street,
            frm_partner.street2 or "",
            frm_partner.city,
            frm_partner.state_id.code,
            frm_partner.zip,
            frm_partner.country_id.code,
            frm_partner.phone,
            to_partner.name,
            to_partner.street,
            to_partner.street2 or "",
            to_partner.city,
            to_partner.state_id.code,
            to_partner.zip,
            to_partner.country_id.code,
            to_partner.phone,
#             insurance_opt
        )
        print("scheduled_date====44444444444444444444===",values)

        # <<< Quartile Limited

        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        if self.shipstation_order_id:
            res = self.env['ship.station.config'].order_create_shipment_label(
                ship_ids.url, ship_ids.user, ship_ids.password, values)
        else:
            res=self.env['ship.station.config'].create_shipment_label(
                ship_ids.url,ship_ids.user,ship_ids.password,values)
        # Quartile Limited: var never use
        #sale_id=self.env['sale.order'].search([('name','=',stock_browse.origin)])[0]
        attachment_pool = self.env['ir.attachment']
        id = res.get('labelData')
        missing_padding = len(id) % 4
        if missing_padding != 0:
            id += b'=' * (4 - missing_padding)
        data_attach = {
            'name': str(self.name)+'.pdf',
            'datas':id,
            'description': 'Label',
            'res_name': self.name,
            'res_model': 'stock.picking',
            'res_id': self.id,
            'datas_fname': str(self.name),
        }
        print("data_attach----",data_attach)
        
        attach_id = attachment_pool.search([('res_id','=',self.id),('res_name','=',self.name)])
        if not attach_id:
            attach_id = attachment_pool.create(data_attach)
        else:
            attach_result = attach_id.write(data_attach)
            attach_id = attach_id[0]
#       self._context['attach_id'] = attach_id
#       print """""""", base64.decodestring(res.get('labelData'))
        if res.get('trackingNumber') and ship_ids.allow_multiple_label:
            self.write({'carrier_tracking_ref':res.get('trackingNumber'),'carrier_price':res.get('shipmentCost'),'label_done':False})

        elif res.get('trackingNumber') and not ship_ids.allow_multiple_label:
            self.write({'carrier_tracking_ref':res.get('trackingNumber'),'carrier_price':res.get('shipmentCost'),'label_done':True})
            # wiz_act = self.do_transfer()
        return True
    
    @api.one    
    def get_rates(self):
        stock_obj= self.env['stock.picking']
        stock_browse=self
        frm_partner=stock_browse.picking_type_id.warehouse_id.partner_id
        to_partner=stock_browse.partner_id
        # if stock_browse.weight_uom.name=='oz(s)':
        #     weight_uom='ounces'
        # if stock_browse.dim_unit.name=='inch(es)':
        #     unit='inches'
        if not stock_browse.carr_id:
            raise Warning(_('Please Select Carrier '))
        if not stock_browse.weight_ship:
            raise Warning(_('Please select Weight unit '))
        if not stock_browse.dim_width:
            raise Warning(_('Please select Dimension Width'))
        if not stock_browse.dim_length :
            raise Warning(_('Please select Dimension Length '))
        if not stock_browse.dim_height :
            raise Warning(_('Please select Dimension Height '))
        if not frm_partner.zip:
            raise Warning(_('Please set Postal Code for Company '))
        if not to_partner.city:
            raise Warning(_('Please set City for Customer '))
        if not to_partner.zip:
            raise Warning(_('Please set Postal code for Customer'))
        if not to_partner.country_id:
            raise Warning(_('Please set Country for Customer'))  
       
        
        values = \
        """{ "carrierCode": "%s","""% str(stock_browse.carr_id.code)+\
        """ "fromPostalCode":"%s","""%str(frm_partner.zip)+\
        """ "toCountry":"%s","""% str(to_partner.country_id.code)+\
        """ "toPostalCode": "%s", """% str(to_partner.zip)+\
        """ "toCity": "%s","""% str(to_partner.city)+\
        """ "weight": {  "value":%d,"""% int(stock_browse.weight_ship)+\
              """ "units":"%s","""% str(stock_browse.weight_uom.name)+\
              """},"dimensions": { "units": "%s","""%str(stock_browse.dim_unit.name)+\
             """ "length": %d,"""% stock_browse.dim_length+\
             """ "width": %d,"""%stock_browse.dim_width+\
             """ "height": %d,"""%stock_browse.dim_height+\
            """},"confirmation": "delivery" }"""

        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        rate_res=ship_ids.get_rates_api(ship_ids.url,ship_ids.user,ship_ids.password,values)
        for data in rate_res:
            vals={
                  'service_code':data.get('serviceCode'),
                  'shipment_cost':data.get('shipmentCost'),
                  'other_cost':data.get('otherCost'),
                  'stock_id':self.id,
                  }
            service_id=self.env['shipstation.services'].search([('code','=',data.get('serviceCode'))])
            if service_id:
                vals.update({'service_id':service_id.id})
            rate_id=self.env['get.rates.services'].search([('service_code','=',data.get('serviceCode'))])
            if rate_id:
                rate_id.write(vals)
            else:
                self.env['get.rates.services'].create(vals)
                
        return vals
    @api.one
    def mark_as_shipped(self):
        stock_obj=self.env['stock.picking']
        stock_browse=self
        order_id=self.env['sale.order'].search([('name','=',stock_browse.origin)])[0].order_id
        print("order_id====",order_id)
        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        values = \
        """{ "orderId": "%s","""%self.shipstation_order_id+\
        """ "carrierCode":"%s","""%str(stock_browse.carr_id.code)+\
        """ "shipDate":"%s","""% str(stock_browse.ship_date)+\
        """ "trackingNumber":%s}"""%str(stock_browse.carrier_tracking_ref)
        print("values-=----",values)
        rate_res=ship_ids.mark_shipped(ship_ids.url,ship_ids.user,ship_ids.password,values)
        print("rate_res====",rate_res)
        return values
    
    
    def get_packages(self):
        carrierCode=self.carrier_code
        ship_ids = self.env['ship.station.config'].search([('id','=',1)])
        res=ship_ids.get_packages_api(ship_ids.url,ship_ids.user,ship_ids.password,carrierCode)    
        return res

stock_picking()

class get_rates_services(models.Model):
    _name='get.rates.services'
    
    service_id=fields.Many2one('shipstation.services','Service Name')
    service_code=fields.Char('Service Code')
    shipment_cost=fields.Float('Shipment Cost')
    other_cost=fields.Float('Other Cost')
    stock_id=fields.Many2one('stock.picking','Stock ID')
    

   
class ProcurementRule(models.Model):
     _inherit = 'procurement.rule'
     
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
  
     @api.model
     def create(self,vals):
         res=super(ProcurementRule,self).create(vals)
         return res     
  
ProcurementRule()   
 
class stock_move(models.Model):
    _inherit='stock.move'    
    
    initial_demamd = fields.Float(string="Remaining Demand") 
 
    

# class ProcurementOrder(models.Model):
#     _inherit = "procurement.order"
# 
#     notes = fields.Text('Notes',size=300 )
#     status = fields.Selection([('shipping','Shipped'),('voided','Voided'),('return','Returned')],'Status')
#     ship_date = fields.Date('Ship Date')
#     carr_id = fields.Many2one('shipstatn.carrier','Carrier Code')
#     service_id=fields.Many2one('shipstation.services','Service Code')
#     package_code= fields.Char('Package Code')
#     weight_ship= fields.Float('Weight')
#     weight_uom= fields.Many2one('product.uom','Unit of Measurement')
#     dim_unit= fields.Many2one('product.uom','Units')
#     dim_length=fields.Float('Length')
#     dim_width= fields.Float('Width')
#     dim_height=fields.Float('Height')
#     is_shipstation=fields.Boolean('Is shipstation')
# 
#     @api.model
#     def create(self,vals):
#         res=super(ProcurementOrder,self).create(vals)
#         return res     
# 
# ProcurementOrder()

    
