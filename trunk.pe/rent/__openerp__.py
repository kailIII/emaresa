# -*- coding: utf-8 -*-
##############################################################################
#
# Author: OpenDrive Ltda
# Copyright (c) 2013 Opendrive Ltda
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
	'name': 'Rent Orders',
	'version': '2.3.1',
	'category': 'Sales Management',
	'sumary': 'Sales Orders, Invoicing',
	'description': """
RENT
====
This module manages the leasing of products to partners.

Modified by David Acevedo Toledo (Fedoro).
Modified by Diego Cantos Zúñiga (Cantoz).
modified by Patricio Felipe Caceres (kron623)
""",
	'author': '[UIDE/WE2BS, OpenDrive Ltda]',
	'website': '[http://www.opendrive.cl]',
	'depends': ['base', 'sale', 'stock', 'purchase', 'web_m2x_options'],
	'data': [
		'security/ir.model.access.csv',
		'report/report_rent.xml',
		'rent_workflow.xml',
		'product_view.xml',
		'rent_view.xml',
		'rent_data.xml',
		'partner_view.xml',
	],
	'css' : [
		'static/src/css/rent.css'
	],
	'installable': True,
}
