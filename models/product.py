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
import json
class product_product(models.Model):
    _inherit = 'product.product'
    
    product_ship_id = fields.Char('Product ID')
    default_cost=fields.Integer('Default Cost')
    length=fields.Integer('Length')
    width=fields.Integer('Width')
    height=fields.Integer('Height')
    weight_oz=fields.Integer('Weight Oz')
    fulfillment_sku=fields.Char('Fulfillment Sku')
    product_type=fields.Char('Product Type')
    default_carrier_code=fields.Char('Default Carrier Code')
    default_service_code=fields.Char('Default Service Code')
    default_pckg_code=fields.Char('Default Package Code')
    df_intl_carriercode=fields.Char('Def.Intl Carrier Code')
    df_intl_servicecode=fields.Char('Def.Intl Service Code')
    df_intl_pckge_code=fields.Char('Def.Intl Package Code')
    customs_descrptn=fields.Char('Customs Description')
    customs_tariff_no=fields.Char('Customs Tariff No')
    customs_country_code=fields.Char('Customs Country Code')
    is_shipstation=fields.Boolean('Is shipstation')

    @api.multi    
    def create_product(self,product_id=False):
        print('uct_id=====',product_id)
        prod_obj=self.env['product.product']
        shipstation_api=self.env['ship.station.config']
        ship_ids = shipstation_api.search([('id','=',1)])
        if not product_id:
            prod_respnse=shipstation_api.get_products_api(ship_ids.url,ship_ids.user,ship_ids.password)
            # self.create_product(prod_respnse.get('products')[0].get('productId'))
        else:
            prod_respnse=[shipstation_api.get_products_api(ship_ids.url,ship_ids.user,ship_ids.password,product_id)]
        for prod_data in prod_respnse:
            if  prod_data:
                if isinstance(prod_data, dict):
                    prod_data = prod_data
                # elif isinstance(prod_data, dict):
                #     prod_data = prod_data
                else:
                    prod_data = prod_respnse.get('products')[0]
                print('prod_data===11', prod_data)
            print('prod_data===22', prod_data)
            prod_vals={
                       'name':prod_data.get('name'),
                       'product_ship_id':prod_data.get('productId'),
                       'default_code':prod_data.get('sku'),
                       'lst_price':prod_data.get('price'),
                       'default_cost':prod_data.get('defaultCost'),
                       'length':prod_data.get('length'),
                       'width':prod_data.get('width'),
                       'height':prod_data.get('height'),
                       'weight_oz':prod_data.get('weightOz'),
                       'fulfillment_sku':prod_data.get('fulfillmentSku'),
                       'create_date':prod_data.get('createDate'),
                       'modified_date':prod_data.get('modifyDate'),
                       'active':prod_data.get('active'),
                       'product_type':prod_data.get('productType'),
                       'default_carrier_code':prod_data.get('defaultCarrierCode'),
                       'default_service_code':prod_data.get('defaultServiceCode'),
                       'default_pckg_code':prod_data.get('default_pckg_code'),
                       'df_intl_carriercode':prod_data.get('defaultIntlCarrierCode'),
                       'df_intl_servicecode':prod_data.get('defaultIntlServiceCode'),
                       'df_intl_pckge_code':prod_data.get('defaultIntlPackageCode'),
                       'customs_descrptn':prod_data.get('customsDescription'),
                       'customs_tariff_no':prod_data.get('customsTariffNo'),
                       'customs_country_code':prod_data.get('customsTariffNo'),
                       'type':"product",
                       'is_shipstation':True,
                       'property_account_income_id':1
                       }
            print("prod_vals===>>",prod_vals)
            prod_id=prod_obj.search([('default_code','=',prod_data.get('sku'))])
            if not prod_id:
                product_id=prod_obj.create(prod_vals)
            else:
                prod_id.write(prod_vals)
                product_id=prod_id
        return product_id