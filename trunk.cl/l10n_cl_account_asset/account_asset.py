# -*- encoding: utf-8 -*-
#
# Author: OpenDrive Ltda
# Copyright (c) 2014 Opendrive Ltda
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

from osv import osv, fields
import time

class asset_asset_depresiation_line(osv.osv):
	_inherit = 'account.asset.depreciation.line'

	def confirm_group_lines(self, cr, uid, ids, move_id, context=None):
		can_close = False
		if context is None:
			context = {}
		asset_obj = self.pool.get('account.asset.asset')
#		period_obj = self.pool.get('account.period')
#		move_obj = self.pool.get('account.move')
#		move_line_obj = self.pool.get('account.move.line')
#		currency_obj = self.pool.get('res.currency')
#		created_move_ids = []
		asset_ids = []
		for line in self.browse(cr, uid, ids, context=context):
			depreciation_date = context.get('depreciation_date') or time.strftime('%Y-%m-%d')
			ctx = dict(context, account_period_prefer_normal=True)
#			period_ids = period_obj.find(cr, uid, depreciation_date, context=ctx)
#			company_currency = line.asset_id.company_id.currency_id.id
#			current_currency = line.asset_id.currency_id.id
			context.update({'date': depreciation_date})
#			amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
#			sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
			asset_name = line.asset_id.name
#			reference = line.name
#			move_vals = {
#				'name': asset_name,
#				'date': depreciation_date,
#				'ref': reference,
#				'period_id': period_ids and period_ids[0] or False,
#				'journal_id': line.asset_id.category_id.journal_id.id,
#			}
#			move_id = move_obj.create(cr, uid, move_vals, context=context)
#			journal_id = line.asset_id.category_id.journal_id.id
#			partner_id = line.asset_id.partner_id.id
#			move_line_obj.create(cr, uid, {
#				'name': asset_name,
#				'ref': reference,
#				'move_id': move_id,
#				'account_id': line.asset_id.category_id.account_depreciation_id.id,
#				'debit': 0.0,
#				'credit': amount,
#				'period_id': period_ids and period_ids[0] or False,
#				'journal_id': journal_id,
#				'partner_id': partner_id,
#				'currency_id': company_currency != current_currency and  current_currency or False,
#				'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
#				'date': depreciation_date,
#			})
#			move_line_obj.create(cr, uid, {
#				'name': asset_name,
#				'ref': reference,
#				'move_id': move_id,
#				'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
#				'credit': 0.0,
#				'debit': amount,
#				'period_id': period_ids and period_ids[0] or False,
#				'journal_id': journal_id,
#				'partner_id': partner_id,
#				'currency_id': company_currency != current_currency and  current_currency or False,
#				'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
#				'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
#				'date': depreciation_date,
#				'asset_id': line.asset_id.id
#			})
			self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
#			created_move_ids.append(move_id)
			asset_ids.append(line.asset_id.id)
		# we re-evaluate the assets to determine whether we can close them
		for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
			if not asset.value_residual:
#			if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
				asset.write({'state': 'close'})
#		return created_move_ids
		return asset_ids
asset_asset_depresiation_line()

#class asset_asset(osv.osv):
#	_inherit = 'account.asset.asset'

#	_columns = {
#		'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic account'),
#	}
#asset_asset()
