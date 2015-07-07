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

class stock_cur_change_standard_price(osv.osv):
	_inherit = 'stock.change.standard.price'

	def change_price(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids[0], context=context)
		usr_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		prod_obj = self.pool.get('product.product').browse(cr, uid, context.get('active_id', False), context=context)

		self.pool.get('product.product').write(cr, uid, context.get('active_id', False),\
			 {'currency_standard_price': wizard.new_price / usr_obj.company_id.currency_id.rate * prod_obj.currency_id.rate},\
							context=context)

		return super(stock_cur_change_standard_price, self).change_price(cr, uid, ids, context=context)
		
stock_cur_change_standard_price()

