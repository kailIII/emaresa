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

class voucher_fields(osv.osv):
	_inherit = 'account.voucher'

##################################################################################################################################################
##################################################################################################################################################
########################################### Elimina la conciliacion y la cantidad de lineas en pagos #############################################
##################################################################################################################################################
##################################################################################################################################################
	def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
		"""
		Returns a dict that contains new values and context

		@param partner_id: latest value from user input for field partner_id
		@param args: other arguments
		@param context: context arguments, like lang, time zone

		@return: Returns a dict which contains new values, and context
		"""
		def _remove_noise_in_o2m():
			"""if the line is partially reconciled, then we must pay attention to display it only once and
				in the good o2m.
				This function returns True if the line is considered as noise and should not be displayed
			"""
			if line.reconcile_partial_id:
				if currency_id == line.currency_id.id:
					if line.amount_residual_currency <= 0:
						return True
				else:
					if line.amount_residual <= 0:
						return True
			return False

		if context is None:
			context = {}
		context_multi_currency = context.copy()

		currency_pool = self.pool.get('res.currency')
		move_line_pool = self.pool.get('account.move.line')
		partner_pool = self.pool.get('res.partner')
		journal_pool = self.pool.get('account.journal')
		line_pool = self.pool.get('account.voucher.line')

		#set default values
		default = {
			'value': {'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
		}

		#drop existing lines
		line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
		if line_ids:
			line_pool.unlink(cr, uid, line_ids)

		if not partner_id or not journal_id:
			return default

		journal = journal_pool.browse(cr, uid, journal_id, context=context)
		partner = partner_pool.browse(cr, uid, partner_id, context=context)
		currency_id = currency_id or journal.company_id.currency_id.id

		total_credit = 0.0
		total_debit = 0.0
		account_type = 'receivable'
		if ttype == 'payment':
			account_type = 'payable'
			total_debit = price or 0.0
		else:
			total_credit = price or 0.0
			account_type = 'receivable'

		if not context.get('move_line_ids', False):
			ids = move_line_pool.search(cr, uid, [('state','=','valid'),\
				('account_id.type', '=', account_type), ('reconcile_id', '=', False),\
				('partner_id', '=', partner_id)], context=context)
		else:
			ids = context['move_line_ids']
		invoice_id = context.get('invoice_id', False)
		company_currency = journal.company_id.currency_id.id
		move_line_found = False

		#order the lines by most old first
		ids.reverse()
		account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

		#compute the total debit/credit and look for a matching open amount or invoice
		for line in account_move_lines:
			if _remove_noise_in_o2m():
				continue

			if invoice_id:
				if line.invoice.id == invoice_id:
					#if the invoice linked to the voucher line is equal to the invoice_id in context
					#then we assign the amount on that line, whatever the other voucher lines
					move_line_found = line.id
					break
			elif currency_id == company_currency:
				#otherwise treatments is the same but with other field names
				if line.amount_residual == price:
					#if the amount residual is equal the amount voucher, we assign it to that voucher
					#line, whatever the other voucher lines
					move_line_found = line.id
					break
				#otherwise we will split the voucher amount on each line (by most old first)
				total_credit += line.credit or 0.0
				total_debit += line.debit or 0.0
			elif currency_id == line.currency_id.id:
				if line.amount_residual_currency == price:
					move_line_found = line.id
					break
				total_credit += line.credit and line.amount_currency or 0.0
				total_debit += line.debit and line.amount_currency or 0.0

		#voucher line creation
		for line in account_move_lines:

			if _remove_noise_in_o2m():
				continue

			if line.currency_id and currency_id == line.currency_id.id:
				amount_original = abs(line.amount_currency)
				amount_unreconciled = abs(line.amount_residual_currency)
			else:
				#always use the amount booked in the company currency as the basis of the conversion into the voucher currency
				amount_original = currency_pool.compute(cr, uid, company_currency, currency_id,\
							line.credit or line.debit or 0.0, context=context_multi_currency)
				amount_unreconciled = currency_pool.compute(cr, uid, company_currency,\
							currency_id, abs(line.amount_residual), context=context_multi_currency)
			line_currency_id = line.currency_id and line.currency_id.id or company_currency
			rs = {
				'centro_costo': line.invoice.out_invoice_cc if line.invoice else '',
				'name':line.move_id.name,
				'type':line.credit and 'dr' or 'cr',
				'move_line_id':line.id,
				'move_line_name':line.name,
				'account_id':line.account_id.id,
				'amount_original': amount_original,
				'amount':(move_line_found == line.id) and min(abs(price), amount_unreconciled) or 0.0,
				'date_original':line.date,
				'date_due':line.date_maturity,
				'amount_unreconciled':amount_unreconciled,
				'currency_id':line_currency_id,
			}
			##################### CONDICION AGREGADA #####################
			if partner.reconcile:
				if 'active_model' not in context.keys():
					rs['amount'] = 0.0
				else:
					if context['active_model'] == 'account.voucher':
						rs['amount'] = 0.0
				
			##############################################################
			#in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
			#on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
			if not move_line_found:
				if currency_id == line_currency_id:
					if line.credit:
						amount = min(amount_unreconciled, abs(total_debit))
						##################### CONDICION AGREGADA #####################
						if partner.reconcile:
							if 'active_model' in context.keys():
								if context['active_model'] != 'account.voucher':
									rs['amount'] = amount
						else:
							rs['amount'] = amount
						##############################################################
						total_debit -= amount
					else:
						amount = min(amount_unreconciled, abs(total_credit))
						##################### CONDICION AGREGADA #####################
						if partner.reconcile:
							if 'active_model' in context.keys():
								if context['active_model'] != 'account.voucher':
									rs['amount'] = amount
						else:
							rs['amount'] = amount
						##############################################################
						total_credit -= amount
			
			if rs['amount_unreconciled'] == rs['amount']:
		####################################### CONDICION AGREGADA ##########################################
				if partner.reconcile:
					if 'active_model' in context.keys():
						if context['active_model'] != 'account.voucher':
							rs['reconcile'] = True
				else:
					rs['reconcile'] = True
		#####################################################################################################

			if rs['type'] == 'cr':
				default['value']['line_cr_ids'].append(rs)
			else:
				default['value']['line_dr_ids'].append(rs)

			if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
				default['value']['pre_line'] = 1
			elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
				default['value']['pre_line'] = 1
			default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
#			raise osv.except_osv('','Aki')
		return default

#####################################################################################################################################
#####################################################################################################################################
########################################### Valida asiento creado en pagos ##########################################################
#####################################################################################################################################
#####################################################################################################################################
	def action_move_line_create(self, cr, uid, ids, context=None):
		'''
		Confirm the vouchers given in ids and create the journal entries for each of them
		'''
		if context is None:
			context = {}
		move_pool = self.pool.get('account.move')
		move_line_pool = self.pool.get('account.move.line')
		for voucher in self.browse(cr, uid, ids, context=context):
			if voucher.move_id:
				continue
			company_currency = self._get_company_currency(cr, uid, voucher.id, context)
			current_currency = self._get_current_currency(cr, uid, voucher.id, context)
			# we select the context to use accordingly if it's a multicurrency case or not
			context = self._sel_context(cr, uid, voucher.id, context)
			# But for the operations made by _convert_amount, we always need to give the date in the context
			ctx = context.copy()
			ctx.update({'date': voucher.date})
			# Create the account move record.
			move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
			# Get the name of the account_move just created
			name = move_pool.browse(cr, uid, move_id, context=context).name
			# Create the first line of the voucher
			move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id,\
								move_id, company_currency, current_currency, context), context)
			move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
			line_total = move_line_brw.debit - move_line_brw.credit
			rec_list_ids = []
			if voucher.type == 'sale':
				line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
			elif voucher.type == 'purchase':
				line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
			# Create one move line per voucher line where amount is not 0.0
			line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id,\
								line_total, move_id, company_currency, current_currency,context)
			
			# Create the writeoff line if needed
			ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id,\
								line_total, move_id, name, company_currency, current_currency, context)
			if ml_writeoff:
				move_line_pool.create(cr, uid, ml_writeoff, context)
			# We post the voucher.
			self.write(cr, uid, [voucher.id], {
				'move_id': move_id,
				'state': 'posted',
				'number': name,
			})
			if voucher.journal_id.entry_posted:
				move_pool.post(cr, uid, [move_id], context={})
			# We automatically reconcile the account move lines.
			reconcile = False
			for rec_ids in rec_list_ids:
				if len(rec_ids) >= 2:
					reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids,\
								writeoff_acc_id=voucher.writeoff_acc_id.id,\
								writeoff_period_id=voucher.period_id.id,\
								writeoff_journal_id=voucher.journal_id.id)

	######################################################################################################
	############################### Asentamos y Validamos el Movimiento ##################################
	######################################################################################################
			move_pool.post(cr, uid, [move_id], context=ctx)
	######################################################################################################
	######################################################################################################
		return True

	def _get_cc(self, cr, uid, ids, name, args, context=None):
		res = {}
		cc = ''
		amount = 0

		for id in ids:
			for voucher in self.browse(cr, uid, ids, context=context):
				for line in voucher.line_ids:
					if line.amount != 0 and line.amount > amount and (line.centro_costo or line.code):
						cc = line.move_line_id.invoice.out_invoice_cc
						amount = line.amount

			res[id] = cc
		return res

	_columns = {
		'date_transfer':fields.date('Fecha Transferencia', readonly=True, states={'draft':[('readonly',False)]}),
		'origin_bank':fields.many2one('res.bank','Banco Origen', readonly=True, states={'draft':[('readonly',False)]}),
#		'code_analytic_id':fields.many2one('account.analytic.account', 'Cost Center'),
#		'code_analytic':fields.related('code_analytic_id', 'code', string='Code', readonly=True,\
#							type='char', relation='account.analytic.account', store=True),
		'code_analytic':fields.function(_get_cc, string='Code', type='char', method=True),
	}

	_defaults = {
		'date_due': lambda *a: time.strftime('%Y-%m-%d'),
	}
voucher_fields() 

class voucher_line_fields(osv.osv):
	_inherit = 'account.voucher.line'

	_columns = {
		'move_line_name':fields.related('move_line_id', 'name', type='char', relation='account.move.line', string='Name', readonly=True),
		'code':fields.related('move_line_id', 'invoice', 'out_invoice_cc', type='char', relation='account.invoice',\
						string='Centro de Costo', readonly=True, store=True),
		'centro_costo':fields.char('Centro de Costo', size=10),
	}
voucher_line_fields() 
