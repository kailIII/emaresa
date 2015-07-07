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

from osv import fields,osv
import openerp.addons.decimal_precision as dp

class product_product(osv.osv):
	_inherit = 'product.product'

	def _replacement_amount(self, cr, uid, ids, field_name, arg, context=None):
		res = {}

		for product in self.browse(cr, uid, ids, context=context):
			res[product.id] = product.currency_standard_price * product.product_tmpl_id.company_id.currency_id.rate

		return res

	_columns = {
		'currency_id':fields.many2one('res.currency', 'Currency'),
		'currency_standard_price':fields.float('Currency Cost Price'),
		'replacement_cost':fields.function(_replacement_amount, digits_compute=dp.get_precision('Account'), string='Replacement Cost'),
	}

	_defaults = {
		'currency_standard_price': 0.0,
	}
product_product()

