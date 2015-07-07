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

class purchase_cost_order_replacement_cost(osv.osv):
	_inherit = 'purchase.cost.order'

	def action_calculated2done(self, cr, uid, ids, context=None):
		if not context:
			context = {}

		res = super(purchase_cost_order_replacement_cost, self).action_calculated2done(cr, uid, ids, context=context)

		#################################### ADD THE CURRENCY STANDARD COST UPDATE #####################################
		for order in self.browse(cr, uid, ids, context=context):
			for line in order.cost_line:
				price = (((line.product_id.qty_available - line.product_qty) * line.product_id.currency_standard_price) \
					+ (line.product_qty * (line.product_id.currency_standard_price + (line.cost_ratio \
					/ order.company_id.currency_id.rate * line.product_id.currency_id.rate)))) / line.product_id.qty_available

				self.pool.get('product.product').write(cr, uid, [line.product_id.id], {'currency_standard_price': price})
#	(line.cost_ratio / line.company_id.currency_id.rate * line.product_id.currency_id.rate) + line.product_id.currency_standard_price
		###################################### FIN CURRENCY STANDARD COST UPDATE #######################################

		return res
purchase_cost_order_replacement_cost()

