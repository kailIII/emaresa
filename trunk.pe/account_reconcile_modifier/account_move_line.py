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

import time
from osv import osv, fields

class account_move_reconcile_comment(osv.osv):
	_inherit = 'account.move.line'

	def reconcile_partial_comment(self, cr, uid, ids, type='auto', context=None, writeoff_acc_id=False, writeoff_period_id=False,\
					writeoff_journal_id=False):
		"""
			Funcion creada para devolver el id de la conciliacion parcial y no True desde la creacion, se hace con una nueva\n
			ya que no se quiere intervenir el proceso naturan de OpenERP.
		"""
		move_rec_obj = self.pool.get('account.move.reconcile')
		merges = []
		unmerge = []
		total = 0.0
		merges_rec = []
		company_list = []
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			if company_list and not line.company_id.id in company_list:
				raise osv.except_osv(_('Warning!'), _('To reconcile the entries company should be the same for all entries.'))
			company_list.append(line.company_id.id)

		for line in self.browse(cr, uid, ids, context=context):
			if line.account_id.currency_id:
				currency_id = line.account_id.currency_id
			else:
				currency_id = line.company_id.currency_id
			if line.reconcile_id:
				raise osv.except_osv(_('Warning'),\
					_("Journal Item '%s' (id: %s), Move '%s' is already reconciled!") % (line.name,\
													line.id, line.move_id.name))
			if line.reconcile_partial_id:
				for line2 in line.reconcile_partial_id.line_partial_ids:
					if not line2.reconcile_id:
						if line2.id not in merges:
							merges.append(line2.id)
						if line2.account_id.currency_id:
							total += line2.amount_currency
						else:
							total += (line2.debit or 0.0) - (line2.credit or 0.0)
				merges_rec.append(line.reconcile_partial_id.id)
			else:
				unmerge.append(line.id)
				if line.account_id.currency_id:
					total += line.amount_currency
				else:
					total += (line.debit or 0.0) - (line.credit or 0.0)
		if self.pool.get('res.currency').is_zero(cr, uid, currency_id, total):
			res = self.reconcile(cr, uid, merges+unmerge, context=context, writeoff_acc_id=writeoff_acc_id,\
						writeoff_period_id=writeoff_period_id, writeoff_journal_id=writeoff_journal_id)
			return res
		r_id = move_rec_obj.create(cr, uid, {
				'type': type,
				'line_partial_ids': map(lambda x: (4,x,False), merges+unmerge)
			}, context=context)
		move_rec_obj.reconcile_partial_check(cr, uid, [r_id] + merges_rec, context=context)
		return r_id

