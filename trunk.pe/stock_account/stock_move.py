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
 
from osv import osv, fields
from tools.translate import _

class stock_move_analytic(osv.osv):
	_inherit = 'stock.move'
	
	_columns = {
		'account_move_id':fields.many2one('account.move', 'Journal Entry'),
	}

	def _create_product_valuation_moves(self, cr, uid, move, context=None):
		"""
		Generate the appropriate accounting moves if the product being moves is subject
		to real_time valuation tracking, and the source or destination location is
		a transit location or is outside of the company.
		"""

		move_obj = self.pool.get('account.move')
		move_line_obj = self.pool.get('account.move.line')
		account_obj = self.pool.get('account.account')

		if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?
			if context is None:
				context = {}
			src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
			dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)
			account_moves = []
			# Outgoing moves (or cross-company output part)
			if move.location_id.company_id \
				and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
					or move.location_id.company_id != move.location_dest_id.company_id):
				journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
				reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
				#returning goods to supplier
				if move.location_dest_id.usage == 'supplier':
					account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
				else:
					account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]

			# Incoming moves (or cross-company input part)
			if move.location_dest_id.company_id \
				and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
					or move.location_id.company_id != move.location_dest_id.company_id):
				journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
				reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
				#goods return from customer
				if move.location_id.usage == 'customer':
					account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
				else:
					account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]
			for j_id, move_lines in account_moves:
				journal_obj = self.pool.get('account.journal').browse(cr, uid, j_id, context=context)
				account_move_id = move_obj.create(cr, uid, {'journal_id': j_id,
							'line_id': move_lines,
							'ref': move.picking_id and move.picking_id.name,})

			self.write(cr, uid, [move.id], {'account_move_id': account_move_id}, context=context)

		return True
stock_move_analytic()
