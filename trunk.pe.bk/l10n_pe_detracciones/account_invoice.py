# -*- coding: utf-8 -*-
##############################################################################
#
# Author: OpenDrive Ltda
# Copyright (c) 2014 Opendrive Ltda
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
from openerp.tools.translate import _
import time
 
class account_invoice_fields(osv.osv):
	_inherit = 'account.invoice'

	def action_move_create(self, cr, uid, ids, context=None):
		"""Creates invoice related analytics and financial move lines"""
		ait_obj = self.pool.get('account.invoice.tax')
		cur_obj = self.pool.get('res.currency')
		period_obj = self.pool.get('account.period')
		payment_term_obj = self.pool.get('account.payment.term')
		journal_obj = self.pool.get('account.journal')
		move_obj = self.pool.get('account.move')
		if context is None:
		    context = {}
		for inv in self.browse(cr, uid, ids, context=context):
		    if not inv.journal_id.sequence_id:
			raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
		    if not inv.invoice_line:
			raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
		    if inv.move_id:
			continue
	
		    ctx = context.copy()
		    ctx.update({'lang': inv.partner_id.lang})
		    if not inv.date_invoice:
			self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
		    company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
		    # create the analytical lines
		    # one move line per invoice line
		    iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
		    # check if taxes are all computed
		    compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
		    self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

		    # I disabled the check_total feature
		    group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
		    group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
		    if group_check_total and uid in [x.id for x in group_check_total.users]:
			if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
			    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

		    if inv.payment_term:
			total_fixed = total_percent = 0
			for line in inv.payment_term.line_ids:
			    if line.value == 'fixed':
				total_fixed += line.value_amount
			    if line.value == 'procent':
				total_percent += line.value_amount
			total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
			if (total_fixed + total_percent) > 100:
			    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

		    # one move line per tax line
		    iml += ait_obj.move_line_get(cr, uid, inv.id)

		    entry_type = ''
		    if inv.type in ('in_invoice', 'in_refund'):
			ref = inv.reference
			entry_type = 'journal_pur_voucher'
			if inv.type == 'in_refund':
			    entry_type = 'cont_voucher'
		    else:
			ref = self._convert_ref(cr, uid, inv.number)
			entry_type = 'journal_sale_vou'
			if inv.type == 'out_refund':
			    entry_type = 'cont_voucher'

		    diff_currency_p = inv.currency_id.id <> company_currency
		    # create one move line for the total and possibly adjust the other lines amount
		    total = 0
		    total_currency = 0
		    total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
		    acc_id = inv.account_id.id

		    name = inv['name'] or inv['supplier_invoice_number'] or '/'
		    totlines = False
		    if inv.payment_term:
			totlines = payment_term_obj.compute(cr,
				uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
		    if totlines:
			res_amount_currency = total_currency
			i = 0
			ctx.update({'date': inv.date_invoice})
			for t in totlines:
			    if inv.currency_id.id != company_currency:
				amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
			    else:
				amount_currency = False

			    # last line add the diff
			    res_amount_currency -= amount_currency or 0
			    i += 1
			    if i == len(totlines):
				amount_currency += res_amount_currency

#######################################################################################################################################
############################################## Agregado para detracciones #############################################################
#######################################################################################################################################
			    if inv.subject_to_detrac:
				    iml.append({
					'type': 'dest',
					'name': name,
					'price': t[1] * inv.detrac_id.porcentaje/100,
					'account_id': inv.detrac_id.account_id.id,
					'date_maturity': t[0],
					'amount_currency': diff_currency_p \
						and amount_currency or False,
					'currency_id': diff_currency_p \
						and inv.currency_id.id or False,
					'ref': ref,
				    })
				    iml.append({
					'type': 'dest',
					'name': name,
					'price': t[1] * (100 - inv.detrac_id.porcentaje)/100,
					'account_id': acc_id,
					'date_maturity': t[0],
					'amount_currency': diff_currency_p \
						and amount_currency or False,
					'currency_id': diff_currency_p \
						and inv.currency_id.id or False,
					'ref': ref,
				    })
			    else:
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
				    iml.append({
					'type': 'dest',
					'name': name,
					'price': t[1],
					'account_id': acc_id,
					'date_maturity': t[0],
					'amount_currency': diff_currency_p \
						and amount_currency or False,
					'currency_id': diff_currency_p \
						and inv.currency_id.id or False,
					'ref': ref,
				    })


		    else:
#######################################################################################################################################
############################################## Agregado para detracciones #############################################################
#######################################################################################################################################
			if inv.subject_to_detrac:
				iml.append({
				    'type': 'dest',
				    'name': name,
				    'price': total * inv.detrac_id.porcentaje/100,
				    'account_id': inv.detrac_id.account_id.id,
				    'date_maturity': inv.date_due or False,
				    'amount_currency': diff_currency_p \
					    and total_currency or False,
				    'currency_id': diff_currency_p \
					    and inv.currency_id.id or False,
				    'ref': ref
				})
				iml.append({
				    'type': 'dest',
				    'name': name,
				    'price': total * (100 - inv.detrac_id.porcentaje)/100,
				    'account_id': acc_id,
				    'date_maturity': inv.date_due or False,
				    'amount_currency': diff_currency_p \
					    and total_currency or False,
				    'currency_id': diff_currency_p \
					    and inv.currency_id.id or False,
				    'ref': ref
				})
			else:
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
				iml.append({
				    'type': 'dest',
				    'name': name,
				    'price': total,
				    'account_id': acc_id,
				    'date_maturity': inv.date_due or False,
				    'amount_currency': diff_currency_p \
					    and total_currency or False,
				    'currency_id': diff_currency_p \
					    and inv.currency_id.id or False,
				    'ref': ref
				})

		    date = inv.date_invoice or time.strftime('%Y-%m-%d')

		    part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

		    line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

		    line = self.group_lines(cr, uid, iml, line, inv)

		    journal_id = inv.journal_id.id
		    journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
		    if journal.centralisation:
			raise osv.except_osv(_('User Error!'),
				_('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

		    line = self.finalize_invoice_move_lines(cr, uid, inv, line)

		    move = {
			'ref': inv.reference and inv.reference or inv.name,
			'line_id': line,
			'journal_id': journal_id,
			'date': date,
			'narration': inv.comment,
			'company_id': inv.company_id.id,
		    }
		    period_id = inv.period_id and inv.period_id.id or False
		    ctx.update(company_id=inv.company_id.id,
			      account_period_prefer_normal=True)
		    if not period_id:
			period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
			period_id = period_ids and period_ids[0] or False
		    if period_id:
			move['period_id'] = period_id
			for i in line:
			    i[2]['period_id'] = period_id

		    ctx.update(invoice=inv)
		    move_id = move_obj.create(cr, uid, move, context=ctx)
		    new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
		    # make the invoice point to that move
		    self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
		    # Pass invoice in context in method post: used if you want to get the same
		    # account move reference when creating the same invoice after a cancelled one:
		    move_obj.post(cr, uid, [move_id], context=ctx)
		self._log_event(cr, uid, ids)
		return True
		
	_columns = {
		'subject_to_detrac':fields.boolean('Considera Detracciones?'),
		'detrac_id':fields.many2one('account.detracciones', 'Services Subject to Detraccion'),
	}

	_defaults = {
		'subject_to_detrac' : lambda *a: False,
	}
account_invoice_fields()

