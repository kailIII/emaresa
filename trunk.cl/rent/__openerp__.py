# -*- encoding: utf-8 -*-
#
# OpenERP Rent - A rent module for OpenERP 6
# Copyright (C) 2010-Today Thibaut DIRLIK <thibaut.dirlik@gmail.com>
# Copyright (C) 2013-David Acevedo Toledo <dacevedo@stratanet.cl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

{
    'name': 'Rent Orders',
    'version': '1.0',
    'category': 'Sales Management',
    'sumary': 'Sales Orders, Invoicing',
    'description':
    """
    This module manages the leasing of products to partners.
    """,
    'author': '[UIDE/WE2BS, Modified by: David Acevedo Toledo/Stratanet Ltda. for OpenDrive Ltda.]',
    'website': 'http://www.stratanet.cl',
    'depends': ['openlib', 'sale', 'stock', 'purchase', 'report_aeroo_ooo'],
    'data': ['uoms_data.xml', 'product_view.xml', 'data/intervals.xml', 'rent_view.xml',
		'menus_view.xml', 'views/sequence.xml', 'rent_workflow.xml', 'security/ir.model.access.csv',
		'report/report_rent.xml', 'pricelist_data.xml'], #, 'data/cron.xml'],
    'css' : ['static/src/css/rent.css'],
    'installable': True,
    'application': True,
    'auto_install': False
    
}
