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

from openerp.osv import osv, fields
from openerp.tools.translate import _

class Product(osv.osv):
	def check_rent_price(self, cr, uid, ids, context=None):
		"""
		We check that the rent price is neither empty or 0 if the product can be rent.
		"""

		products = self.browse(cr, uid, ids, context=context)
		
		for product in products:
			if product.can_be_rent:
				if not product.rent_price or product.rent_price <= 0:
					return False

		return True

	def onchange_rentable_product(self, cr, uid, ids, rent_time_unity, context=None):
		"""
		Returns the default price unity (the first in the list).
		"""
		if not rent_time_unity:
			unity_id = self.pool.get('product.uom').search(cr, uid, [('name','=','Day')], limit=1, context=context)
			if unity_id:
				return {
					'value': {
						'rent_time_unity': unity_id[0]
					}
				}
		return {}
    
	def default_time_unity(self, cr, uid, context=None):
		"""
		Returns the default price unity (the first in the list).
		"""

		unity_id = self.pool.get('product.uom').search(cr, uid, [('name','=','Day')], limit=1, context=context)

		if unity_id:
			return unity_id[0]

		return False

	_name = 'product.product'
	_inherit = 'product.product'

	_columns = {
		'can_be_rent':fields.boolean('Can be rented', help='Enable this if you want to rent this product.'),
		'rent_price':fields.float('Rent price',\
				help='The price is expressed for the duration unity defined in the company configuration.'),
		'rent_time_unity':fields.many2one('product.uom', 'Rent Time Unity',
					help='Rent duration unity in which the price is defined.'),
 #domain=[('category_id.name', '=', 'Duration')],
	}

	_defaults = {
		'can_be_rent' : False,
		'rent_price' : 1.0,
#		'rent_time_unity' : default_time_unity
	}

	_constraints = [(check_rent_price, _('The Rent price must be a positive value.'), ['rent_price'])]

Product()

