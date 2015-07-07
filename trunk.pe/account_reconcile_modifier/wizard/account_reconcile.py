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

class account_reconcile_inherit(osv.osv_memory):
	_inherit = 'account.move.line.reconcile'

	_columns = {
		'comment':fields.text('Comment'),
	}

	def trans_rec_reconcile_full_comment(self, cr, uid, ids, context=None):
		mod_obj = self.pool.get('ir.model.data')
		period_obj = self.pool.get('account.period')
		account_move_line_obj = self.pool.get('account.move.line')

		if context is None:
			context = {}

		date = False
		period_id = False
		journal_id= False
		account_id = False
		
		date = time.strftime('%Y-%m-%d')
		ctx = dict(context or {}, account_period_prefer_normal=True)
		ids = period_obj.find(cr, uid, dt=date, context=ctx)
		if ids:
			period_id = ids[0]

		context.update({'reconcile_id': account_move_line_obj.reconcile(cr, uid, context['active_ids'], 'manual', account_id,\
							period_id, journal_id, context=context)})

		model_data_ids = mod_obj.search(cr, uid,[('model','=','ir.ui.view'),\
				('name','=','view_account_move_line_reconcile_comment_full')], context=context)
		resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

		return {
			'name': 'Ingrese Comentario',
			'context': context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.move.line.reconcile',
			'views': [(resource_id,'form')],
			'type': 'ir.actions.act_window',
			'target': 'new',
		}

	def trans_rec_reconcile_full(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids)[0]
		
		if 'reconcile_id' in context:
			self.pool.get('account.move.reconcile').write(cr, uid, [ context['reconcile_id'] ],\
							{'comment': wizard.comment}, context=context)

		return {'type': 'ir.actions.act_window_close'}

	def trans_rec_reconcile_partial_comment(self, cr, uid, ids, context=None):
		mod_obj = self.pool.get('ir.model.data')
		if context is None:
			context = {}

		model_data_ids = mod_obj.search(cr, uid,[('model','=','ir.ui.view'),\
				('name','=','account_move_line_reconcile_writeoff_comment')], context=context)
		resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

		return {
			'name': 'Ingrese Comentario',
			'context': context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.move.line.reconcile.writeoff.comment',
			'views': [(resource_id,'form')],
			'type': 'ir.actions.act_window',
			'target': 'new',
		}
account_reconcile_inherit()


class account_move_line_reconcile_writeoff_comment(osv.osv_memory):
	"""
		Funcion de paso para no instanciar la vista de account.move.line.reconcile.writeoff, de lo contrario llamaria\n
		los campos requeridos y no permite guardar el comentario.
	"""
	_name = 'account.move.line.reconcile.writeoff.comment'

	_columns = {
		'comment_partial':fields.text('Comment', size=64),
	}

	def trans_rec_reconcile_partial(self, cr, uid, ids, context=None):
		context.update({'comment_partial': self.browse(cr, uid, ids)[0].comment_partial})
		return self.pool.get('account.move.line.reconcile.writeoff').trans_rec_reconcile_partial(cr, uid, ids, context)

account_move_line_reconcile_writeoff_comment()

class account_move_reconcile_comment(osv.osv):
	_inherit = 'account.move.line'

	def reconcile_partial_comment(self, cr, uid, ids, type='auto', context=None, writeoff_acc_id=False, writeoff_period_id=False,\
					writeoff_journal_id=False):
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

class account_move_line_reconcile_writeoff_comment(osv.osv_memory):
	_inherit = 'account.move.line.reconcile.writeoff'

	def trans_rec_reconcile_partial(self, cr, uid, ids, context=None):
		account_move_line_obj = self.pool.get('account.move.line')
		reconcile_id = account_move_line_obj.reconcile_partial_comment(cr, uid, context['active_ids'], 'manual', context=context)

		if reconcile_id and 'comment_partial' in context:
			self.pool.get('account.move.reconcile').write(cr, uid, [reconcile_id],\
								{'comment': context['comment_partial']}, context=context)

		return {'type': 'ir.actions.act_window_close'}
		

	def trans_rec_reconcile(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids)[0]
		account_move_line_obj = self.pool.get('account.move.line')
		period_obj = self.pool.get('account.period')
		if context is None:
			context = {}

		data = self.read(cr, uid, ids,context=context)[0]
		account_id = data['writeoff_acc_id'][0]
		context['date_p'] = data['date_p']
		journal_id = data['journal_id'][0]
		context['comment'] = data['comment']
		if data['analytic_id']:
			context['analytic_id'] = data['analytic_id'][0]
		if context['date_p']:
			date = context['date_p']
		context['account_period_prefer_normal'] = True
		ids = period_obj.find(cr, uid, dt=date, context=context)
		if ids:
			period_id = ids[0]

		reconcile_id = account_move_line_obj.reconcile(cr, uid, context['active_ids'], 'manual', account_id,
							period_id, journal_id, context=context)

		self.pool.get('account.move.reconcile').write(cr, uid, [reconcile_id],\
									{'comment': data['comment']}, context=context)
		
		return {'type': 'ir.actions.act_window_close'}
account_move_line_reconcile_writeoff_comment()

