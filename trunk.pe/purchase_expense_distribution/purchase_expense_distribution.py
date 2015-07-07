# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import osv, fields


class purchase_cost_expense_type(osv.osv):
	_name = "purchase.cost.expense.type"
	_description = "Purchase Expenses Types"

	_columns = {
		'name':fields.char('Name', size=128, required=True, translate=True, select=True),
		'ref':fields.char('Reference', size=64, required=True, select=True),
		'company_id': fields.many2one('res.company', 'Company', required=True, select=1),
		'default_expense': fields.boolean('Default Expense',
							help="Specify if the expense can be automatic selected in a purchase cost order."),
		'calculation_method': fields.selection([('amount', 'Amount line'),
							('price', 'Product price'),
							('qty', 'Product quantity'),
							('weight', 'Product weight'),
							('weight_net', 'Product weight net'),
							('volume', 'Product Volume'),
							('equal', 'Equal to')], 'Calculation Method'),
		'note': fields.text('Cost Documentation'),
	}

	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr,\
											    uid, 'purchase.cost.type', context=c),
		'calculation_method': 'amount',
		'default_expense': False,
	}

	def unlink(self, cr, uid, ids, context=None):
		order_expenses = self.pool.get('purchase.cost.order.expense').search(cr, uid, [('type_id', 'in', ids)])
		if order_expenses:
			raise osv.except_osv(_('Invalid Action!'), _('You can not delete expense type, is being used!'))
		      
		return osv.osv.unlink(self, cr, uid, ids, context=context)
purchase_cost_expense_type()

class purchase_cost_order(osv.osv):
	def _recalculate_all(self, cr, uid, ids, field_name, arg, context=None):
		res = {}

		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'uom_qty': 0.0,
				'weight': 0.0,
				'weight_net': 0.0,
				'purchase_amount': 0.0,
				'purchase_amount_currency': 0.0,
				'volume': 0.0,
				'product_price_amount': 0.0,
			}

			val1 = val2 = val3 = val4 = val4_currency = val5 = val6 = val6_currency = 0.0

			for line in order.cost_line:
				val1 += line.product_qty
				val2 += line.product_id.weight * line.product_qty
				val3 += line.product_id.weight_net * line.product_qty
				val4 += line.product_qty * line.product_price_unit
				val4_currency += line.product_qty * line.product_price_unit / order.currency_id.rate
				val5 += line.product_volume * line.product_price_unit
				val6 += line.product_price_unit
				val6_currency += line.product_price_unit / order.currency_id.rate

			res[order.id]['uom_qty'] = val1
			res[order.id]['weight'] = val2
			res[order.id]['weight_net'] = val3
			res[order.id]['purchase_amount'] = val4
			res[order.id]['purchase_amount_currency'] = val4_currency
			res[order.id]['volume'] = val5
			res[order.id]['product_price_amount'] = val6
			res[order.id]['product_price_amount_currency'] = val6_currency
			res[order.id]['amount_total'] = val4 + order.expense_amount
			res[order.id]['amount_total_currency'] = val4_currency + order.expense_amount_currency
		return res

	def _amount_expense(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		val = 0.0
		for order in self.browse(cr, uid, ids, context=context):
			for expenseline in order.expense_line:
				val += expenseline.expense_amount
		res[order.id] = val

		return res

	def _amount_expense_currency(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		val = 0.0
		for order in self.browse(cr, uid, ids, context=context):
			for expenseline in order.expense_line:
				val += expenseline.expense_amount_currency
		res[order.id] = val

		return res

	def _expense_id_default(self, cr, uid, ids, context=None):
		expense_type_ids = []
		expense_ids = self.pool.get('purchase.cost.expense.type').search(cr, uid, [('default_expense', '=', True)], context=context)
		if expense_ids:
			for expense in expense_ids:
				res = {
					'type_id': expense
				}
				expense_type_ids.append(res)
			return expense_type_ids
		return False

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('purchase.cost.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	def _get_expenses(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('purchase.cost.order.expense').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	def _get_currency(self, cr, uid, context=None):
		currency_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id
		res = currency_id
		return res

	_name = 'purchase.cost.order'
	_description = 'Purchase Cost Order'
	_order = 'name desc'
	
	_columns = {
		'name':fields.char('Name', size=128, required=True, translate=True, select=True),
		'ref':fields.char('Reference', size=64, select=True),
		'currency_id':fields.many2one('res.currency', 'Currency', help="The optional other currency if it is a multi-currency entry."),
		'account_journal_id':fields.many2one('account.journal', 'Account Journal', required=True),
		'move_id':fields.many2one('account.move', 'Account Move', ondelete='cascade'),
		'company_id':fields.many2one('res.company', 'Company', required=True, select=1),
		'state':fields.selection([('draft', 'Draft Order'),
						('calculated', 'Order Calculated'),
						('done', 'Done'),
						('error', 'Error'),
						('cancel', 'Cancel')], 'Status', readonly=True),
		'cost_update_type':fields.selection([('direct', 'Direct Update')], 'Cost Update Type'),
		'date_order':fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
		'uom_qty':fields.function(_recalculate_all, digits_compute = dp.get_precision('Product UoS'), string ='Order Quantity',\
						store = {
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'weight':fields.function(_recalculate_all, digits_compute = dp.get_precision('Stock Weight'), string='Order Gross Weight',\
						help="The gross weight in Kg.",
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'weight_net':fields.function(_recalculate_all, digits_compute = dp.get_precision('Stock Weight'), string='Order Net Weight',\
						readonly=True, help="The net weight in Kg.",
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'volume':fields.function(_recalculate_all, string='Order Volume', readonly=True, help="The volume in m3.",
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'purchase_amount':fields.function(_recalculate_all, digits_compute = dp.get_precision('Account'), string='Purchase Total',
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'amount_total':fields.function(_recalculate_all, digits_compute = dp.get_precision('Account'), string='Total',
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'expense_amount':fields.function(_amount_expense, digits_compute = dp.get_precision('Account'), string='Expense Amount',
						store={
							'purchase.cost.order.expense': (_get_expenses, None, 20),
						}),
		'note':fields.text('Documentation for this order'),
		'expense_line':fields.one2many('purchase.cost.order.expense', 'order_id', 'Cost Distributions', ondelete="cascade"),
		'cost_line':fields.one2many('purchase.cost.order.line', 'order_id', 'Order Lines', ondelete="cascade"),
		'cost_line_currency':fields.one2many('purchase.cost.order.line', 'order_id', 'Order Lines', ondelete="cascade"),
		'lognote':fields.text('Log process for this order', readonly=True),
		'log_line':fields.one2many('purchase.cost.order.log', 'order_id', 'Log Lines', ondelete="cascade"),
		'product_price_amount':fields.function(_amount_expense, digits_compute = dp.get_precision('Account'),
						string='Product unit amount',
						store = {
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, muti='totals'),
		#################################### NEW FIELDS FOR USD #######################################
		'purchase_amount_currency':fields.function(_recalculate_all, digits_compute = dp.get_precision('Account'),\
						string='Purchase Total (Currency)',\
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'amount_total_currency':fields.function(_recalculate_all, digits_compute = dp.get_precision('Account'),\
						string='Total (Currency)',
						store={
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, multi='totals'),
		'expense_amount_currency':fields.function(_amount_expense_currency, digits_compute = dp.get_precision('Account'),\
						string='Expense Amount (Currency)',\
						store={
							'purchase.cost.order.expense': (_get_expenses, None, 20),
						}),
		'product_price_amount_currency':fields.function(_amount_expense_currency, digits_compute = dp.get_precision('Account'),\
						string='Product unit amount (Currency)',\
						store = {
							'purchase.cost.order': (lambda self, cr, uid, ids, c={}: ids, ['cost_line'], 10),
							'purchase.cost.order.line': (_get_order, None, 20),
						}, muti='totals'),
		################################## END NEW FIELDS FOR USD #####################################
	}

	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.company').\
									_company_default_get(cr, uid, 'purchase.cost.order', context=c),
		'date_order': fields.date.context_today,
		'expense_line': _expense_id_default,
		'currency_id': _get_currency,
		'name': lambda obj, cr, uid, context: '/',
		'state': 'draft',
		'cost_update_type': 'direct',
	}

	def unlink(self, cr, uid, ids, context=None):
		cost_orders = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for c in cost_orders:
			if c['state'] in ['draft', 'calculated']:
				unlink_ids.append(c['id'])
			else:
				raise osv.except_osv(_('Invalid Action!'), _('In order to delete a confirmed cost order!'))

		return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

	def create(self, cr, uid, vals, context=None):
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.cost.order') or '/'

		return super(purchase_cost_order, self).create(cr, uid, vals, context=context)

	def action_button_copy(self, cr, uid, ids, context=None):
		res_id = self.pool.get('purchase.cost.wizard').create(cr, uid, {'state': 'step1'}, context=context)
		mod_obj = self.pool.get('ir.model.data')
		res = mod_obj.get_object_reference(cr, uid, 'purchase_expense_distribution', 'purchase_cost_wizard_view')
		view_id = res and res[1] or False,
		context.update({'cost_order_id': ids[0]})

		return {
			'name': _('Please select Supplier'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'res_model': 'purchase.cost.wizard',
			'type': 'ir.actions.act_window',
			'res_id': res_id,
			'nodestroy': True,
			'target': 'new',
			'context': context,
		}

	def button_dummy(self, cr, uid, ids, context=None):
		return True

	################################################################################################
	def _create_account_move_line(self, cr, uid, line, move_id, context=None):
		"""
		Generate the account.move.line values to track the landed cost.
		"""
		aml_obj = self.pool.get('account.move.line')
		aml_obj.create(cr, uid, {'name': line.name,
					'move_id': move_id,
					'product_id': line.product_id.id,
					'quantity': line.product_qty,
					'debit': line.expense_amount,
					'account_id': line.product_id.product_tmpl_id.categ_id.property_stock_valuation_account_id.id
				}, context=context)
		aml_obj.create(cr, uid, {'name': line.name,
					'move_id': move_id,
					'product_id': line.product_id.id,
					'quantity': line.product_qty,
					'credit': line.expense_amount,
					'account_id': line.product_id.property_account_expense and line.product_id.property_account_expense.id or\
								line.product_id.product_tmpl_id.categ_id.property_stock_account_input_categ.id
				}, context=context)
		return True

	def _create_account_move(self, cr, uid, order, context=None):
		vals = {
			'journal_id': order.account_journal_id.id,
			'period_id': self.pool.get('account.period').find(cr, uid, order.date_order, context=context)[0],
			'date': order.date_order,
			'ref': order.ref or order.name
		}
		return self.pool.get('account.move').create(cr, uid, vals, context=context)
	###############################################################################################

	def action_draft2calculated(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			# Check expense lines for amount 0
			for expense in order.expense_line:
				if expense.expense_amount == 0.0:
					raise osv.except_osv(_('ERROR EXPENSE!'), _('Please enter amount for this expense: "%s" (amount:%d)') % \
										      (expense.type_id.name, expense.expense_amount))
				if expense.expense_amount_currency == 0.0:
					raise osv.except_osv(_('ERROR EXPENSE!'), _('Please enter amount for this expense: "%s" (amount:%d)') % \
										      (expense.type_id.name, expense.expense_amount_currency))
			#Check if exist lines in order
			if not order.cost_line:
				raise osv.except_osv(_('ERROR NOT LINES!'), _('No shipping lines in this order'))
			#Check data for expense type call check_datas function
			check_datas = self.test_datas_out_log(cr, uid, ids, context)
			if check_datas == True:
				self.write(cr, uid, [order.id], {'state': 'error'}, context=context)
				return False

			# Calculating expense line
			for expense in order.expense_line:
				if expense.type_id.calculation_method == 'amount':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = (expense.expense_amount * line.amount) / order.purchase_amount
						amount_currency = (expense.expense_amount_currency * line.amount_currency) \
										/ order.purchase_amount_currency
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
				if expense.type_id.calculation_method == 'price':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = (expense.expense_amount * line.product_price_unit) / order.product_price_amount
						amount_currency = (expense.expense_amount_currency * line.product_price_unit_currency)\
											/ order.product_price_amount_currency
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
				if expense.type_id.calculation_method == 'qty':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = (expense.expense_amount * line.product_qty) / order.uom_qty
						amount_currency = (expense.expense_amount_currency * line.product_qty) / order.uom_qty
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
				if expense.type_id.calculation_method == 'weight':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = (expense.expense_amount * line.amount_weight) / order.weight
						amount_currency = (expense.expense_amount_currency * line.amount_weight) / order.weight
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
				if expense.type_id.calculation_method == 'weight_net':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = (expense.expense_amount * line.amount_weight_net) / order.weight_net
						amount_currency = (expense.expense_amount_currency * line.amount_weight_net) / order.weight_net
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
				if expense.type_id.calculation_method == 'volume':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = (expense.expense_amount * line.amount_volume) / order.volume
						amount_currency = (expense.expense_amount_currency * line.amount_volume) / order.volume
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
				if expense.type_id.calculation_method == 'equal':
					for line in order.cost_line:
						cost_ratio = 0.0
						cost_ratio_currency = 0.0
						amount = 0.0
						amount_currency = 0.0

						amount = expense.expense_amount / len(order.cost_line)
						amount_currency = expense.expense_amount_currency / len(order.cost_line)
						cost_ratio = amount / line.product_qty
						cost_ratio_currency = amount_currency / line.product_qty

						res = {
							'expense_id': expense.id,
							'order_line_id': line.id,
							'expense_amount': amount,
							'expense_amount_currency': amount_currency,
							'cost_ratio': cost_ratio,
							'cost_ratio_currency': cost_ratio_currency,
							'type_id': expense.type_id.id,
						}
						self.pool.get('purchase.cost.order.line.expense').create(cr, uid, res, context=context)
						res.clear()
		#Calculate cost_rate, expense_amount_ standard_price_new per line
		for line in order.cost_line:
			cost_ratio = 0.0
			cost_ratio_currency = 0.0
			expense_amount = 0.0
			expense_amount_currency = 0.0
			standard_price_new = 0.0
			standard_price_new_currency = 0.0

			for expense in line.expense_line:
				cost_ratio = cost_ratio + expense.cost_ratio
				cost_ratio_currency = cost_ratio_currency + expense.cost_ratio_currency
				expense_amount = expense_amount + expense.expense_amount
				expense_amount_currency = expense_amount_currency + expense.expense_amount_currency

#			standard_price_new = line.standard_price_old + cost_ratio
			standard_price_new = (((line.product_id.qty_available - line.product_qty) * line.standard_price_old) \
					+ (line.product_qty * (line.standard_price_old + cost_ratio))) / line.product_id.qty_available
			standard_price_new_currency = (((line.product_id.qty_available - line.product_qty) * line.standard_price_old_currency) \
				+ (line.product_qty * (line.standard_price_old_currency + cost_ratio_currency))) / line.product_id.qty_available

			line.write({
				    'cost_ratio': cost_ratio,
				    'cost_ratio_currency': cost_ratio_currency,
				    'expense_amount': expense_amount,
				    'expense_amount_currency': expense_amount_currency,
				    'standard_price_new': standard_price_new,
				    'standard_price_new_currency': standard_price_new_currency
			})

		#Write log line and change order state
		res = {
			'name': 'Calculation log %s' % (time.strftime('%Y-%m-%d %H:%M:%S')),
			'order_id': order.id,
			'state': 'done',
			'date_log': time.strftime('%Y-%m-%d %H:%M:%S'),
			'lognote': _('Calculation is Done'),
		}
		self.pool.get('purchase.cost.order.log').create(cr, uid, res, context=context)
		self.write(cr, uid, [order.id], {'state': 'calculated'}, context=context)

		return True

	def action_calculated2done(self, cr, uid, ids, context=None):
		if not context:
			context = {}

		for order in self.browse(cr, uid, ids, context=context):
			################### CREA EL ASIENTO ####################
			move_id = self._create_account_move(cr, uid, order, context=context)
			########################################################
			for line in order.cost_line:
				product_obj = self.pool.get('product.product')
				product_obj.write(cr, uid, [line.product_id.id], {'standard_price': line.standard_price_new})
				######################## CREA LINEA DEL ASIENTO ##########################
				self._create_account_move_line(cr, uid, line, move_id, context=context)
				##########################################################################

		self.write(cr, uid, [order.id], {'state': 'done', 'move_id': move_id}, context=context)
		res = {
			'name': 'Calculation log %s' % (time.strftime('%Y-%m-%d %H:%M:%S')),
			'order_id': order.id,
			'state': 'update',
			'date_log': time.strftime('%Y-%m-%d %H:%M:%S'),
			'lognote': _('Update Cost price of products is Done'),
		}
		self.pool.get('purchase.cost.order.log').create(cr, uid, res, context=context)
		return True

	def test_datas_out_log(self, cr, uid, ids, context=None):
		test_result = False
		logtext = ""
		for order in self.browse(cr, uid, ids, context=context):
			#Check mandatory totals
			if order.purchase_amount == 0.0:
				test_result = True
				logtext += _('Missing total purchase amount.\n')
			if order.uom_qty == 0.0:
				test_result = True
				logtext += _('Missing total purchase qty.\n')
			if order.expense_amount == 0.0:
				test_result = True
				logtext += _('Missing total expense amount.\n')
			#Check mandatory data in lines for expense type
			for expense in order.expense_line:
				if expense.type_id.calculation_method == 'amount':
					line_num = 1
					for line in order.cost_line:
						if line.amount == 0.0:
							test_result = True
							logtext += _('Missing total in line %s product %s.\n' % (line_num, line.name))
							line_num = line_num + 1
				elif expense.type_id.calculation_method == 'price':
					line_num = 1
					for line in order.cost_line:
						if line.product_price_unit == 0.0:
							test_result = True
							logtext += _('Missing product price in line %s product %s.\n' % (line_num, line.name))
							line_num = line_num + 1
				elif expense.type_id.calculation_method == 'qty':
					if order.uom_qty == 0.0:
						test_result = True
						logtext += _('Missing total purchase qty.\n')
					line_num = 1
					for line in order.cost_line:
						if line.product_qty == 0.0:
							test_result = True
							logtext += _('Missing product qty in line %s product %s.\n' % (line_num, line.name))
							line_num = line_num + 1
				elif expense.type_id.calculation_method == 'weight':
					if order.weight == 0.0:
						test_result = True
						logtext += _('Missing total purchase weight.\n')
					line_num = 1
					for line in order.cost_line:
						if line.product_weight == 0.0:
							test_result = True
							logtext += _('Missing product weight in line %s product %s.\n' % (line_num, line.name))
							line_num = line_num + 1
				elif expense.type_id.calculation_method == 'weight_net':
					if order.weight_net == 0.0:
						test_result = True
						logtext += _('Missing total purchase weight net.\n')
					line_num = 1
					for line in order.cost_line:
						if line.product_weight_net == 0.0:
							test_result = True
							logtext += _('Missing product weight net in line %s product %s.\n' % (line_num, line.name))
							line_num = line_num + 1
				elif expense.type_id.calculation_method == 'volume':
					if order.volume == 0.0:
						test_result = True
						logtext += _('Missing total purchase volume.\n')
					line_num = 1
					for line in order.cost_line:
						if line.product_volume == 0.0:
							test_result = True
							logtext += _('Missing product volume in line Id %s product %s.\n' % (line_num, line.name))
							line_num = line_num + 1
		#Write log field
		if test_result == True:
			res = {
				'name': 'Calculation log %s' % (time.strftime('%Y-%m-%d %H:%M:%S')),
				'order_id': order.id,
				'state': 'error',
				'date_log': time.strftime('%Y-%m-%d %H:%M:%S'),
				'lognote': logtext,
			}
			self.pool.get('purchase.cost.order.log').create(cr, uid, res, context=context)
		return test_result

	def action_calculated2draft(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			if order.move_id:
				self.pool.get('account.move').unlink(cr, uid, [order.move_id.id], context=context)

			expense_line_ids = []
			for line in order.cost_line:
				for expense in line.expense_line:
					expense_line_ids.append(expense.id)
		expense_line_obj = self.pool.get('purchase.cost.order.line.expense')
		expense_line_obj.unlink(cr, uid, expense_line_ids)
		res = {
			'name': 'Calculation log %s' % (time.strftime('%Y-%m-%d %H:%M:%S')),
			'order_id': order.id,
			'state': 'draft',
			'date_log': time.strftime('%Y-%m-%d %H:%M:%S'),
			'lognote': _('The Order has been changed from Calculated to Draft by the action of cancel button'),
		}
		self.pool.get('purchase.cost.order.log').create(cr, uid, res, context=context)
		self.write(cr, uid, [order.id], {'state': 'draft'}, context=context)
		return True
purchase_cost_order()

class purchase_cost_order_log(osv.osv):
	_name = "purchase.cost.order.log"
	_descripction = "Purchase Cost Order Calculate Log"
	_order = "id desc"

	_columns = {
		'order_id': fields.many2one('purchase.cost.order', 'Cost Order', select=True, ondelete="cascade"),
		'name': fields.char('Name', size=128, required=True, translate=True, select=True),
		'state': fields.selection([('error', 'Calculation Error'),
						('done', 'Calculation Done'),
						('update','Update products cost Done'),
						('draft', 'Order return in Draft')], 'Status', readonly=True),
		'date_log': fields.date('Date', required=True, readonly=True, select=True),
		'lognote': fields.text('Description', readonly=True),
	}
purchase_cost_order_log()

class purchase_cost_order_expense(osv.osv):
	_name = "purchase.cost.order.expense"
	_description = "Purchase Cost Expenses"

	def onchange_expense_amount(self, cr, uid, ids, expense_amount, context=None):
		if not context:
			context = {}

		if not 'currency_id' in context:
			return {}

		currency = self.pool.get('res.currency').browse(cr, uid, context['currency_id'], context=context)

		expense_amount_currency = expense_amount / currency.rate if currency else 1

		return {
			'value': {
				'expense_amount_currency': expense_amount_currency
			}
		}

	_columns = {
		'order_id': fields.many2one('purchase.cost.order', 'Cost Order', select=True, ondelete="cascade"),
		'type_id': fields.many2one('purchase.cost.expense.type', 'Expense Type', select=True, ondelete="set null"),
		'expense_amount': fields.float('Expense Amount', digits_compute=dp.get_precision('Account'), required=True),
		'expense_amount_currency': fields.float('Expense Amount (Currency)', digits_compute=dp.get_precision('Account'), required=True),
	}

	_defaults = {
		'expense_amount': 0.0,
		'expense_amount_currency': 0.0,
	}
purchase_cost_order_expense()

class purchase_cost_order_line(osv.osv):
	def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		if context is None:
			context = {}

		for line in self.browse(cr, uid, ids, context=context):
			res[line.id] = {
				'amount': 0.0,
				'amount_currency': 0.0,
				'amount_weight': 0.0,
				'amount_weight_net': 0.0,
				'amount_volume': 0.0,
			}

			res[line.id]['amount'] = line.product_qty * line.product_price_unit
			res[line.id]['amount_currency'] = line.product_qty * line.product_price_unit / line.order_id.currency_id.rate
			res[line.id]['amount_weight'] = line.product_weight * line.product_qty
			res[line.id]['amount_weight_net'] = line.product_weight_net * line.product_qty
			res[line.id]['amount_volume'] = line.product_volume * line.product_qty

		return res

	_name = "purchase.cost.order.line"
	_description = "Purchase Cost Order Line"

	_columns = {
		'order_id': fields.many2one('purchase.cost.order', 'Cost Order', ondelete='cascade'),
		'partner_id': fields.many2one('res.partner', 'Supplier', readonly=True, select=True),
		'purchase_id': fields.many2one('purchase.order', 'Purchase Order', ondelete='set null', select=True),
		'purchase_line_id': fields.many2one('purchase.order.line', 'Purchase Order Line', ondelete='set null', select=True),
		'expense_line': fields.one2many('purchase.cost.order.line.expense', 'order_line_id', 'Expenses Distribution line',\
								ondelete='cascade'),
		'expense_line_currency': fields.one2many('purchase.cost.order.line.expense', 'order_line_id',\
								'Expenses Distribution line (Currency)', ondelete='cascade'),
		'picking_id': fields.many2one('stock.picking', 'Picking', ondelete='set null'),
		'move_line_id': fields.many2one('stock.move', 'Picking Line', ondelete="set null"),
		'name': fields.char('Description', required=True, select=True),
		'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
		'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
		'product_uos_qty': fields.float('Quantity (UOS)', digits_compute=dp.get_precision('Product Unit of Measure')),
		'product_uos': fields.many2one('product.uom', 'Product UOS'),
		'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
		'product_price_unit':fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
		'product_volume':fields.float('Volume', help="The volume in m3."),
		'product_weight':fields.float('Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The gross weight in Kg."),
		'product_weight_net':fields.float('Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),
		'amount':fields.function(_amount_line, type='float', multi='lines', string='Amount Line',
						digits_compute=dp.get_precision('Account'),
						store={
							'purchase.cost.order.line':(lambda self, cr, uid, ids, ctx=None: ids, ['product_id'], 10)
						}),
		'standard_price_old': fields.float('Cost', digits_compute=dp.get_precision('Product Price')),
		'expense_amount': fields.float('Cost Amount', digits_compute=dp.get_precision('Account')),
		'cost_ratio':fields.float('Cost Ratio', digits_compute=dp.get_precision('Account')),
		'standard_price_new': fields.float('New Cost', digits_compute=dp.get_precision('Product Price')),
		'company_id':fields.related('order_id', 'company_id', type='many2one', relation='res.company', string='Company',
									store=True, readonly=True),
		'amount_weight':fields.function(_amount_line, type='float', digits_compute=dp.get_precision('Stock Weight'),\
						store={
							'purchase.cost.order.line':(lambda self, cr, uid, ids, ctx=None: ids, ['product_id'], 10)
						}, multi='lines', string='Line Gross Weight', help="The line gross weight in Kg."),
		'amount_weight_net':fields.function(_amount_line, type='float', digits_compute=dp.get_precision('Stock Weight'),\
						store={
							'purchase.cost.order.line':(lambda self, cr, uid, ids, ctx=None: ids, ['product_id'], 10)
						}, multi='lines', string='Line Net Weight', help="The line net weight in Kg."),
		'amount_volume': fields.function(_amount_line, type='float', multi='lines', string='Line Volume',\
						store={
							'purchase.cost.order.line':(lambda self, cr, uid, ids, ctx=None: ids, ['product_id'], 10)
						}, help="The line volume in m3."),
		############################## NEW FIELDS FOR USD #################################
		'product_price_unit_currency':fields.float('Unit Price (Currency)',\
							digits_compute=dp.get_precision('Product Price')), #Nuevo Campo
		'amount_currency':fields.function(_amount_line, type='float', multi='lines', string='Amount Line (Currency)',
						digits_compute=dp.get_precision('Account'),
						store={
						      'purchase.cost.order.line':(lambda self, cr, uid, ids, ctx=None: ids, ['product_id'], 10)
						}), #Nuevo Campo
		'expense_amount_currency':fields.float('Cost Amount (Currency)', digits_compute=dp.get_precision('Account')), #Nuevo Campo
		'cost_ratio_currency':fields.float('Cost Ratio (Currency)', digits_compute=dp.get_precision('Account')), #Nuevo Campo
		'standard_price_new_currency':fields.float('New Cost (Currency)', digits_compute=dp.get_precision('Product Price')), #Nuevo Campo
		'standard_price_old_currency':fields.float('Cost (Currency)', digits_compute=dp.get_precision('Product Price')) #Nuevo Campo
		############################ END NEW FIELDS FOR USD ###############################
	}

	_default = {
		'expense_amount': 0.0,
		'expense_amount_currency': 0.0,
		'cost_ration': 0.0,
		'cost_ratio_currency': 0.0,
		'standard_price_new': 0.0,
		'standard_price_new_currency': 0.0
	}
purchase_cost_order_line()

class purchase_order_line_expense(osv.osv):
	_name = "purchase.cost.order.line.expense"
	_description = "Purchase Expenses Order Line Distribution"

	_columns = {
		'order_line_id': fields.many2one('purchase.cost.order.line', 'Cost Order Line', ondelete="cascade"),
		'expense_id': fields.many2one('purchase.cost.order.expense', 'Expenses Distribution Line', ondelete="cascade"),
		'type_id': fields.many2one('purchase.cost.expense.type', 'Expense Type', select=True, ondelete="set null"),
		'expense_amount': fields.float('Expense Amount Type Line', digits_compute=dp.get_precision('Account')),
		'cost_ratio': fields.float('Cost Amount for Product', digits_compute=dp.get_precision('Account')),
		######################### NEW FIELD FOR USD #########################
		'expense_amount_currency':fields.float('Expense Amount Type Line (Currency)', digits_compute=dp.get_precision('Account')),
		'cost_ratio_currency':fields.float('Cost Amount for Product (Currency)', digits_compute=dp.get_precision('Account')),
		###################### END NEW FIELD FOR USD ########################
	}

	_default = {
		'expense_amount': 0.0,
		'expense_amount_currency': 0.0,
		'cost_ration': 0.0,
		'cost_ration_currency': 0.0,
	}
purchase_order_line_expense()
