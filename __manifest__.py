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

{
    "name" : "Odoo 11 ShipStation Connector",
    "version" : "2.0",
    "depends" : ["stock", "delivery",'document','product','website_sale_delivery'],
    "author" : "Globalteckz",
    "description": """
       Manage your shipping based on services sign-up on Shipstation from Odoo and update to Shipstation.
    """,
    "website" : "http://www.globalteckz.com",
    'images': ['static/description/Banner.png'],
    "category" : "ecommerce",
    "price": "500.00",
    "currency": "EUR",
    'summary': 'Shipstation Integration',
    "demo" : [],
    "data" : [
            'data/get_tracking_id_cron.xml',
            'views/ship_station_config_view.xml',
            'views/delivery_view.xml',
            'views/product_data.xml',
            'views/sale_view.xml',
            'views/product_view.xml',
            'views/shipstation_carrier_view.xml',
            'views/shipstation_tags_view.xml',
#             'stock_picking_view.xml',
            'views/store_marktplce_view.xml',
            'wizard/import_shipped_orders_view.xml',
            'wizard/export_order_to_ship.xml',
            'security/ir.model.access.csv',
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


