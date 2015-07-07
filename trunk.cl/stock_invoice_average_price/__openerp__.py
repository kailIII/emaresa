# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#                       Jesús Martín <jmartin@zikzakmedia.com>
#    
#    Modified for OpenERP v7.0 by Stratanet Ltda. (www.stratanet.cl) and OpenDrive Ltda (www.opendrive.cl), 25/09/2013
#			David Acevedo <dacevedo@stratanet.cl>
#			Paulo Ortiz <portiz@opendrive.cl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Stock Invoice Average Price',
    'version': '0.4',
    'category': 'Generic Modules/Inventory Control',
    'description': """
    This module recompute the cost price of products when its cost method is average price \
and the invoice is validated and the price unit of the supplier picking (old cost price) is \
different to the price unit of the supplier invoice line (new cost price), using\
 this formula:

                                      (current_cost_price x current_stock) - \
(picking_cost_price x picking_qty) + (invoice_cost_price x invoice_qty)
new_average_price = -----------------------------------------------------------\
-------------------------------------------------------------------------------\
------
                                                                               \
current_stock - picking_qty + invoice_qty

    This module also adds a wizard that breaks down the cost of supplier invoices \
(like transport or custom tax) to several products extracted from other supplier \
invoices in order to update the cost price of products when its cost method is \
average price.

    This module was modified, ported and tested for OpenERP v7.0
    """,
    'author': '[Zikzakmedia SL - Modified by: David Acevedo Toledo/Stratanet Ltda.; Paulo Ortiz/OpenDrive Ltda.]',
    'website': 'www.zikzakmedia.com,www.stratanet.cl,www.opendrive.cl',
    'license': 'AGPL-3',
    'depends': ['sale','account','stock'],
    'data' : [
    	'breakdown_sequence.xml',
        'wizard/breakdown_view.xml',
    ],
    'installable': True,
    'active': False,
    'auto_install': False,
    'application': True
}
