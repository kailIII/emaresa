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

class stock_picking_replacement_cost(osv.osv):
	_inherit = 'stock.picking'

	def do_partial(self, cr, uid, ids, partial_datas, context=None):
		res = super(stock_picking_replacement_cost, self).do_partial(cr, uid, ids, partial_datas, context=context)

		product_obj = self.pool.get('product.product')
		currency_obj = self.pool.get('res.currency')
		uom_obj = self.pool.get('product.uom')
		product_avail = {}

		for pick in self.browse(cr, uid, ids, context=context):
			for move in pick.move_lines:
				partial_data = partial_datas.get('move%s'%(move.id), False)
				product_qty = partial_data.get('product_qty',0.0)
				product_price = partial_data.get('product_price',0.0)
				product_currency = partial_data.get('product_currency',False)
				product_uom = partial_data.get('product_uom',False)

				# Average price Currency computation
				if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
					product = product_obj.browse(cr, uid, move.product_id.id)
					move_currency_id = move.company_id.currency_id.id
					context['currency_id'] = move_currency_id

					qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

					if product.id not in product_avail:
						# keep track of stock on hand including processed lines not yet marked as done
						product_avail[product.id] = product.qty_available - qty

					if qty > 0:
						new_price = currency_obj.compute(cr, uid, product_currency,\
											move_currency_id, product_price, round=False)
						new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)

						if product_avail[product.id] <= 0:
							product_avail[product.id] = 0
							new_cur_std_price = new_price / move.company_id.currency_id.rate * product.currency_id.rate
						else:
							# Get the currency standard price
							amount_cur_unit = product.currency_standard_price

							new_cur_std_price = ((amount_cur_unit * product_avail[product.id])\
								+ (new_price / move.company_id.currency_id.rate * product.currency_id.rate * qty))\
								/ (product_avail[product.id] + qty)

						# Write the field according to price type field
						product_obj.write(cr, uid, [product.id], {'currency_standard_price': new_cur_std_price})
		return res
stock_picking_replacement_cost()

class stock_move_replacement_cost(osv.osv):
	_inherit = 'stock.move'

	def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
		res = super(stock_move_replacement_cost, self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=context)

		if move.origin:
			res[0][2]['name'] = move.origin
			res[1][2]['name'] = move.origin

		return res

	def do_partial(self, cr, uid, ids, partial_datas, context=None):
		res = super(stock_move_replacement_cost, self).do_partial(cr, uid, ids, partial_datas, context=context)
		product_obj = self.pool.get('product.product')
		currency_obj = self.pool.get('res.currency')
		uom_obj = self.pool.get('product.uom')

		for move in self.browse(cr, uid, ids, context=context):
			partial_data = partial_datas.get('move%s'%(move.id), False)
			product_qty = partial_data.get('product_qty',0.0)
			product_price = partial_data.get('product_price',0.0)
			product_currency = partial_data.get('product_currency',False)
			product_uom = partial_data.get('product_uom',False)

			# Average price computation
			if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
				product = product_obj.browse(cr, uid, move.product_id.id)
				move_currency_id = move.company_id.currency_id.id
				context['currency_id'] = move_currency_id
				qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

				available = product.qty_available - qty

				if qty > 0:
					new_price = currency_obj.compute(cr, uid, product_currency, move_currency_id, product_price, round=False)
					new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)

					if available <= 0:
						new_cur_std_price = new_price / move.company_id.currency_id.rate * product.currency_id.rate
					else:
						# Get the standard currency price
						amount_cur_unit = product.currency_standard_price

						new_cur_std_price = ((amount_cur_unit * available)\
							+ (new_price / move.company_id.currency_id.rate * product.currency_id.rate * qty))\
								/ (available + qty)

					product_obj.write(cr, uid, [product.id], {'currency_standard_price': new_cur_std_price})
		return res

#	def _update_average_price(self, cr, uid, move, context=None):
#		product_obj = self.pool.get('product.product')
#		currency_obj = self.pool.get('res.currency')
#		uom_obj = self.pool.get('product.uom')
#		product_avail = {}
#
#		if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
#			product = product_obj.browse(cr, uid, move.product_id.id)
#			move_currency_id = move.company_id.currency_id.id
#			context['currency_id'] = move_currency_id
#
#			product_qty = move.product_qty
#			product_uom = move.product_uom.id
#			product_price = move.price_unit
#			product_currency = move.price_currency_id.id
#
#			if product.id not in product_avail:
				# keep track of stock on hand including processed lines not yet marked as done
#				product_avail[product.id] = product.qty_available
#
#			qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
#			if qty > 0:
#				new_price = currency_obj.compute(cr, uid, product_currency, move_currency_id, product_price, round=False)
#				new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)
#				if product_avail[product.id] <= 0:
#					product_avail[product.id] = 0
#					new_std_price = new_price
#					new_cur_std_price = new_price / move.company_id.currency_id.rate * product.currency_id.rate
#				else:
					# Get the standard price
#					amount_unit = product.price_get('standard_price', context=context)[product.id]
#					amount_cur_unit = product.currency_standard_price #price_get('currency_standard_price', context=context)[product.id]

#					new_std_price = ((amount_unit * product_avail[product.id])\
#								+ (new_price * qty))/(product_avail[product.id] + qty)
#					new_cur_std_price = ((amount_cur_unit * product_avail[product.id])\
#							+ (new_price / move.company_id.currency_id.rate * product.currency_id.rate * qty))\
#							/ (product_avail[product.id] + qty)
				
#				product_obj.write(cr, uid, [product.id],{'standard_price': new_std_price,
#									'currency_standard_price': new_cur_std_price})

#				product_avail[product.id] += qty

stock_move_replacement_cost()

