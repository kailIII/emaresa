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
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions

from openerp import netsvc
#from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_honorarios(osv.osv):
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for fees in self.browse(cr, uid, ids, context=context):
            res[fees.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in fees.fees_line:
                res[fees.id]['amount_untaxed'] += line.price_subtotal
            for line in fees.tax_line:
                res[fees.id]['amount_tax'] += line.amount
            res[fees.id]['amount_total'] = res[fees.id]['amount_untaxed'] - res[fees.id]['amount_tax'] 
        return res

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        journal_obj = self.pool.get('account.journal')
        domain = [('company_id', '=', company_id)]
        res = journal_obj.search(cr, uid, domain, limit=1)
        return res and res[0] or False

    def _get_currency(self, cr, uid, context=None):
        res = False
        journal_id = self._get_journal(cr, uid, context=context)
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            res = journal.currency and journal.currency.id or journal.company_id.currency_id.id
        return res

    def _get_journal_analytic(self, cr, uid, type_inv, context=None):
###########################################################################################################################
###########################################################################################################################
#########################Revisar en account/project/project.py por los tipos###############################################
###########################################################################################################################
###########################################################################################################################
        result = self.pool.get('account.analytic.journal').search(cr, uid, ['type','=','purchase'], context=context)
        if not result:
            raise osv.except_osv(_('No Analytic Journal!'),_("You must define an analytic journal (purchase) for ballot fees!"))
        return result[0]

#    def _get_type(self, cr, uid, context=None):
#        if context is None:
#            context = {}
#        return context.get('type', 'out_invoice')

    def _reconciled(self, cr, uid, ids, name, args, context=None):
        res = {}
        wf_service = netsvc.LocalService("workflow")
        for fee in self.browse(cr, uid, ids, context=context):
            res[fee.id] = self.test_paid(cr, uid, [fee.id])
            if not res[fee.id] and fee.state == 'paid':
                wf_service.trg_validate(uid, 'account.fees', fee.id, 'open_test', cr)
        return res

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
	"""Function of the field residua. It computes the residual amount (balance) for each invoice"""
	if context is None:
		context = {}
	ctx = context.copy()
	result = {}
	currency_obj = self.pool.get('res.currency')
	for fees in self.browse(cr, uid, ids, context=context):
		nb_fee_in_partial_rec = max_fees_id = 0
		result[fees.id] = 0.0
		if fees.move_id:
			for aml in fees.move_id.line_id:
				if aml.account_id.type in ('receivable','payable'):
					if aml.currency_id and aml.currency_id.id == fees.currency_id.id:
						result[fees.id] += aml.amount_residual_currency
					else:
						ctx['date'] = aml.date
						result[fees.id] += currency_obj.compute(cr, uid, aml.company_id.currency_id.id, fees.currency_id.id, aml.amount_residual, context=ctx)

					if aml.reconcile_partial_id.line_partial_ids:
						#we check if the ballot fees is partially reconciled and if there are other ballot fees
						#involved in this partial reconciliation (and we sum these ballot fees)
						for line in aml.reconcile_partial_id.line_partial_ids:
							if line.fees:
								nb_fee_in_partial_rec += 1
								#store the max ballot fees id as for this ballot fees we will make a balance instead of a simple division
								max_fees_id = max(max_fees_id, line.fees.id)
		if nb_fee_in_partial_rec:
			#if there are several ballot fees in a partial reconciliation, we split the residual by the number
			#of ballot fees to have a sum of residual amounts that matches the partner balance
			new_value = currency_obj.round(cr, uid, fees.currency_id, result[fees.id] / nb_fee_in_partial_rec)
			if fees.id == max_fees_id:
				#if it's the last the ballo fees of the bunch of ballot fees partially reconciled together, we make a
				#balance to avoid rounding errors
				result[fees.id] = result[fees.id] - ((nb_fee_in_partial_rec - 1) * new_value)
			else:
				result[fees.id] = new_value
				#prevent the residual amount on the ballot fees to be less than 0
		result[fees.id] = max(result[fees.id], 0.0)            
	return result



    # Give Journal Items related to the payment reconciled to this ballot fees
    # Return ids of partial and total payments related to the selected ballot fees
    def _get_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for fees in self.browse(cr, uid, ids, context=context):
            id = fees.id
            res[id] = []
            if not fees.move_id:
                continue
            data_lines = [x for x in fees.move_id.line_id if x.account_id.id == fees.account_id.id]
            partial_ids = []
            for line in data_lines:
                ids_line = []
                if line.reconcile_id:
                    ids_line = line.reconcile_id.line_id
                elif line.reconcile_partial_id:
                    ids_line = line.reconcile_partial_id.line_partial_ids
                l = map(lambda x: x.id, ids_line)
                partial_ids.append(line.id)
                res[id] =[x for x in l if x <> line.id and x not in partial_ids]
        return res

    def _get_fees_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.fees.line').browse(cr, uid, ids, context=context):
            result[line.fees_id.id] = True
        return result.keys()

    def _get_fees_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.fees.tax').browse(cr, uid, ids, context=context):
            result[tax.fees_id.id] = True
        return result.keys()

    def _compute_lines(self, cr, uid, ids, name, args, context=None):
        result = {}
        for fees in self.browse(cr, uid, ids, context=context):
            src = []
            lines = []
            if fees.move_id:
                for m in fees.move_id.line_id:
                    temp_lines = []
                    if m.reconcile_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_id.line_id)
                    elif m.reconcile_partial_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
                    lines += [x for x in temp_lines if x not in lines]
                    src.append(m.id)

            lines = filter(lambda x: x not in src, lines)
            result[fees.id] = lines
        return result

    def _get_fees_from_line(self, cr, uid, ids, context=None):
        move = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        fees_ids = []
        if move:
            fees_ids = self.pool.get('account.fees').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return fees_ids

    def _get_fees_from_reconcile(self, cr, uid, ids, context=None):
        move = {}
        for r in self.pool.get('account.move.reconcile').browse(cr, uid, ids, context=context):
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        fees_ids = []
        if move:
            fees_ids = self.pool.get('account.fees').search(cr, uid, [('move_id','in',move.keys())], context=context)
        return fees_ids

    _name = "account.fees"
    _inherit = ['mail.thread']
    _description = 'Honorarios'
    _order = "id desc"
#    _track = {
#        'type': {
#        },
#        'state': {
#            'account.mt_invoice_paid': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'paid' and obj['type'] in ('out_invoice', 'out_refund'),
#            'account.mt_invoice_validated': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'open' and obj['type'] in ('out_invoice', 'out_refund'),
#        },
#    }
    _columns = {
	'name': fields.char('Description', size=64, select=True, readonly=True),# states={'draft':[('readonly',False)]}),
	'origin': fields.char('Source Document', size=64, help="Reference of the document that produced this ballot fees.",\
		readonly=True), #states={'draft':[('readonly',False)]}),
	'fees_number':fields.char('Fees Number', size=64, help="The reference of this ballot fees as provided by the lender.",\
		readonly=True),# states={'draft':[('readonly',False)]}),
	'number':fields.related('move_id','name', type='char', readonly=True, size=64, relation='account.move',\
		store=True, string='Number'),
	'internal_number':fields.char('Ballot Fees Number', size=32, readonly=True,\
		help="Unique number of the ballot fees, computed automatically when the ballot fees is created."),
	'comment': fields.text('Additional Information'),
	'state':fields.selection([
		('draft','Draft'),\
		('open','Open'),\
		('paid','Paid'),\
		('cancel','Cancelled'),\
		],'Status', select=True, readonly=True, track_visibility='onchange',\
			help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
			\n* The \'Open\' status is used when user create ballot fees,a ballot fees number is generated.Its in open status till user does not pay ballot fees. \
			\n* The \'Paid\' status is set automatically when the ballot fees is paid. Its related journal entries may or may not be reconciled. \
			\n* The \'Cancelled\' status is used when user cancel ballot fees.'),
	'sent': fields.boolean('Sent', readonly=True, help="It indicates that the ballot fees has been sent."),
	'date_fees':fields.date('Ballor Fees Date', readonly=True,\
		select=True, help="Keep empty to use the current date"),
	'partner_id':fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True,\
		track_visibility='always'),
	'payment_term': fields.many2one('account.payment.term', 'Payment Terms',readonly=True,\
		help="If you use payment terms, the due date will be computed automatically at the generation "\
		"of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
		"The payment term may compute several due dates, for example 50% now, 50% in one month."),
	'period_id': fields.many2one('account.period', 'Force Period', \
		domain=[('state','<>','done')],\
		help="Keep empty to use the period of the validation(ballot fees) date.", readonly=True),
	'account_id':fields.many2one('account.account', 'Account', required=True, readonly=True,\
		help="The partner account used for this ballot fees."),
	'fees_line':fields.one2many('account.fees.line', 'fees_id', 'Ballot Fees Lines', readonly=True),
	'tax_line':fields.one2many('account.fees.tax', 'fees_id', 'Tax Lines', readonly=True),
	'move_id':fields.many2one('account.move', 'Journal Entry', readonly=True, select=1, ondelete='restrict',\
		help="Link to the automatically generated Journal Items."),
	'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Bruto', \
		track_visibility='always', store={
			                'account.fees': (lambda self, cr, uid, ids, c={}: ids, ['fees_line'], 20),
			                'account.fees.tax': (_get_fees_tax, None, 20),
			                'account.fees.line': (_get_fees_line,\
						['price_unit','fees_line_tax_id','quantity','discount','fees_id'], 20),
			            }, multi='all'),
	'amount_tax':fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Retencion',\
		store={
			'account.fees': (lambda self, cr, uid, ids, c={}: ids, ['fees_line'], 20),
			'account.fees.tax': (_get_fees_tax, None, 20),
			'account.fees.line': (_get_fees_line, ['price_unit','fees_line_tax_id','quantity','discount','fees_id'], 20),
		}, multi='all'),
	'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total a Pagar',\
		store={
			'account.fees': (lambda self, cr, uid, ids, c={}: ids, ['fees_line'], 20),
			'account.fees.tax': (_get_fees_tax, None, 20),
			'account.fees.line': (_get_fees_line, ['price_unit','fees_line_tax_id','quantity','discount','fees_id'], 20),
		}, multi='all'),
	'currency_id':fields.many2one('res.currency', 'Currency', required=True, readonly=True,\
		track_visibility='always'),
	'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True),
	'check_total': fields.float('Verification Total', digits_compute=dp.get_precision('Account'), readonly=True),
	'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True),
	'reconciled': fields.function(_reconciled, string='Paid/Reconciled', type='boolean',\
		store={
			'account.fees': (lambda self, cr, uid, ids, c={}: ids, None, 50), # Check if we can remove ?
			'account.move.line': (_get_fees_from_line, None, 50),
			'account.move.reconcile': (_get_fees_from_reconcile, None, 50),
		},\
		help="It indicates that the ballot fees has been paid and the journal entry of the ballot fees has been reconciled\
		with one or several journal entries of payment."),
	'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',\
		help='Bank Account Number to which the ballot fees will be paid. A Company bank account if this is a Customer Ballot Fees,\
		otherwise a Partner bank account number.', readonly=True),# states={'draft':[('readonly',False)]}),
	'move_lines':fields.function(_get_lines, type='many2many', relation='account.move.line', string='Entry Lines'),
	'residual': fields.function(_amount_residual, digits_compute=dp.get_precision('Account'), string='Balance',\
		store={
			'account.fees': (lambda self, cr, uid, ids, c={}: ids, ['fees_line','move_id'], 50),
			'account.fees.tax': (_get_fees_tax, None, 50),
			'account.fees.line': (_get_fees_line, ['price_unit','fees_line_tax_id','quantity','discount','fees_id'], 50),
			'account.move.line': (_get_fees_from_line, None, 50),
			'account.move.reconcile': (_get_fees_from_reconcile, None, 50),
		}, help="Remaining amount due."),
	'payment_ids': fields.function(_compute_lines, relation='account.move.line', type="many2many", string='Payments'),
#        'move_name': fields.char('Journal Entry', size=64, readonly=True, states={'draft':[('readonly',False)]}),
	'user_id': fields.many2one('res.users', 'Salesperson', readonly=True, track_visibility='onchange'),
	'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=True),
    }

    _defaults = {
	'state': 'draft',
	'journal_id': _get_journal,
	'currency_id': _get_currency,
	'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
	'check_total': 0.0,
        'internal_number': False,
	'user_id': lambda s, cr, u, c: u,
        'sent': False,
    }

    _sql_constraints = [
        ('number_uniq', 'unique(number, company_id, journal_id)', 'Ballot Fees Number must be unique per Company!'),
    ]


    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
	journal_obj = self.pool.get('account.journal')
	if context is None:
		context = {}

	if context.get('active_model', '') in ['res.partner'] and context.get('active_ids', False) and context['active_ids']:
		partner = self.pool.get(context['active_model']).read(cr, uid, context['active_ids'], ['supplier','customer'])[0]
		if not view_type:
			view_id = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'account.fees.tree')])
			view_type = 'tree'
		if view_type == 'form':
			if partner['supplier'] and not partner['customer']:
				view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', 'account.fees.supplier.form')])
			elif partner['customer'] and not partner['supplier']:
				view_id = self.pool.get('ir.ui.view').search(cr,uid,[('name', '=', 'account.fees.form')])
	if view_id and isinstance(view_id, (list, tuple)):
		view_id = view_id[0]
	res = super(account_honorarios,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

	#######################################OJOOOOOOOOOOOOOOO##############################
	type = context.get('journal_type', False)
	for field in res['fields']:
		if field == 'journal_id' and type:
			journal_select = journal_obj._name_search(cr, uid, '', [('type', '=', type)], context=context, limit=None, name_get_uid=1)
			res['fields'][field]['selection'] = journal_select
	doc = etree.XML(res['arch'])

	return res

    def get_log_context(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'fees_form')
        view_id = res and res[1] or False
        context['view_id'] = view_id
        return context

    def ballot_fees_print(self, cr, uid, ids, context=None):
        '''
        This function prints the ballot fees and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.fees',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.fees',
            'datas': datas,
            'nodestroy' : True
        }


    def action_fees_sent(self, cr, uid, ids, context=None):
	'''
		This function opens a window to compose an email, with the edi invoice template message loaded by default
	'''
	assert len(ids) == 1, 'This option should only be used for a single id at a time.'
	ir_model_data = self.pool.get('ir.model.data')
	try:
		##############################OJO AKIIIIIII######################
		template_id = ir_model_data.get_object_reference(cr, uid, 'account', 'email_template_edi_invoice')[1]
	    ############################################################################################
	except ValueError:
		template_id = False
	try:
		compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
	except ValueError:
		compose_form_id = False
	ctx = dict(context)
	ctx.update({
		'default_model': 'account.fees',
		'default_res_id': ids[0],
		'default_use_template': bool(template_id),
		'default_template_id': template_id,
		'default_composition_mode': 'comment',
		'mark_fees_as_sent': True,
	 })
	return {
		'type': 'ir.actions.act_window',
		'view_type': 'form',
		'view_mode': 'form',
		'res_model': 'mail.compose.message',
		'views': [(compose_form_id, 'form')],
		'view_id': compose_form_id,
		'target': 'new',
		'context': ctx,
	}


    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
	result = {}
	if journal_id:
		journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
		currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
		company_id = journal.company_id.id
		result = {
			'value': {
				'currency_id': currency_id,
				'company_id': company_id,
			}
		}
	return result


    def onchange_company_id(self, cr, uid, ids, company_id, part_id, fees_line, currency_id):
        #TODO: add the missing context parameter when forward-porting in trunk so we can remove
        #      this hack!
        context = self.pool['res.users'].context_get(cr, uid)

        val = {}
        dom = {}
        obj_journal = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        fee_line_obj = self.pool.get('account.fees.line')
        if company_id and part_id and type:
            acc_id = False
            partner_obj = self.pool.get('res.partner').browse(cr,uid,part_id)
            if partner_obj.property_account_payable and partner_obj.property_account_receivable:
                if partner_obj.property_account_payable.company_id.id != company_id and partner_obj.property_account_receivable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr, uid, [('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr, uid, [('name','=','property_account_payable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr, uid, [('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr, uid, [('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr, uid, rec_pro_id, ['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr, uid, pay_pro_id, ['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of account, you should create one from Settings\Configuration\Accounting menu.'))
                    acc_id = rec_res_id
                    val= {'account_id': acc_id}
            if ids:
                if company_id:
                    fee_obj = self.browse(cr,uid,ids)
                    for line in fee_obj[0].fees_line:
                        if line.account_id:
                            if line.account_id.company_id.id != company_id:
                                result_id = account_obj.search(cr, uid, [('name','=',line.account_id.name),('company_id','=',company_id)])
                                if not result_id:
                                    raise osv.except_osv(_('Configuration Error!'),
                                        _('Cannot find a chart of account, you should create one from Settings\Configuration\Accounting menu.'))
                                fee_line_obj.write(cr, uid, [line.id], {'account_id': result_id[-1]})
            else:
                if fees_line:
                    for fee_line in fees_line:
                        obj_l = account_obj.browse(cr, uid, fee_line[2]['account_id'])
                        if obj_l.company_id.id != company_id:
                            raise osv.except_osv(_('Configuration Error!'),
                                _('Ballot fees line account\'s company and ballot fees\'s company does not match.'))
                        else:
                            continue
        if company_id:
            journal_ids = obj_journal.search(cr, uid, [('company_id','=',company_id), ('type', '=', 'purchase')])#AGREGADA CONDICION A MANO
            if journal_ids:
                val['journal_id'] = journal_ids[0]
            ir_values_obj = self.pool.get('ir.values')
	    			################## OJO AKIIII!!!!!  #####################
            res_journal_default = ir_values_obj.get(cr, uid, 'default', 'type=%s' % ('purchase'), ['account.fees'])
            for r in res_journal_default:
                if r[1] == 'journal_id' and r[2] in journal_ids:
                    val['journal_id'] = r[2]
            if not val.get('journal_id', False):
                journal_type_map = dict(obj_journal._columns['type'].selection)
                journal_type_label = self.pool['ir.translation']._get_source(cr, uid, None, ('code','selection'),
                                                                             context.get('lang'),
									     #OJO AK TAMBIEN
                                                                             'purchase')

                raise osv.except_osv(_('Configuration Error!'),
                                     _('Cannot find any account journal of %s type for this company.\n\nYou can create one in the menu: \nConfiguration\Journals\Journals.') % ('"%s"' % journal_type_label))
            dom = {'journal_id':  [('id', 'in', journal_ids)]}
        else:
            journal_ids = obj_journal.search(cr, uid, [])

        return {'value': val, 'domain': dom}


    def unlink(self, cr, uid, ids, context=None):
	if context is None:
		context = {}
	fees = self.read(cr, uid, ids, ['state','internal_number'], context=context)
	unlink_ids = []

	for t in fees:
		if t['state'] not in ('draft', 'cancel'):
			raise openerp.exceptions.Warning(\
				_('You cannot delete an ballot fees which is not draft or cancelled. You should refund it instead.'))
		elif t['internal_number']:
			raise openerp.exceptions.Warning(\
				_('You cannot delete an ballot fees after it has been validated (and received a number).  You can set it back to "Draft" state and modify its content, then re-confirm it.'))
		else:
			unlink_ids.append(t['id'])

	osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
	return True


    def onchange_partner_id(self, cr, uid, ids, partner_id, date_fees=False, payment_term=False,\
    		partner_bank_id=False, company_id=False):
	partner_payment_term = False
	acc_id = False
	bank_id = False
	fiscal_position = False

	opt = [('uid', str(uid))]
	if partner_id:
		opt.insert(0, ('id', partner_id))
		p = self.pool.get('res.partner').browse(cr, uid, partner_id)
		if company_id:
			if (p.property_account_receivable.company_id and\
					(p.property_account_receivable.company_id.id != company_id)) and\
					(p.property_account_payable.company_id and\
					(p.property_account_payable.company_id.id != company_id)):
				property_obj = self.pool.get('ir.property')
				rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
				pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
				if not rec_pro_id:
					rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
				if not pay_pro_id:
					pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
				rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
				pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
				rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
				pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
				if not rec_res_id and not pay_res_id:
					raise osv.except_osv(_('Configuration Error!'),
						_('Cannot find a chart of accounts for this company, you should create one.'))
				account_obj = self.pool.get('account.account')
				rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
				pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
				p.property_account_receivable = rec_obj_acc[0]
				p.property_account_payable = pay_obj_acc[0]

			acc_id = p.property_account_payable.id
			partner_payment_term = p.property_supplier_payment_term and p.property_supplier_payment_term.id or False
			fiscal_position = p.property_account_position and p.property_account_position.id or False
			if p.bank_ids:
				bank_id = p.bank_ids[0].id

	result = {
		'value': {
			'account_id': acc_id,
			'payment_term': partner_payment_term,
			'fiscal_position': fiscal_position
		}
	}

	result['value']['partner_bank_id'] = bank_id

	if payment_term != partner_payment_term:
		if partner_payment_term:
			to_update = self.onchange_payment_term_date_fees(cr, uid, ids, partner_payment_term, date_fees)
			result['value'].update(to_update['value'])

	if partner_bank_id != bank_id:
		to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
		result['value'].update(to_update['value'])

	return result


    def onchange_payment_term_date_fees(self, cr, uid, ids, payment_term_id, date_fees):
	res = {}
	if not date_fees:
		res = {
			'value':{
				'date_fees': time.strftime('%Y-%m-%d')
			}
		}
	return res


#    def onchang_invoice_line(self, cr, uid, ids, lines):
#        return {}


    def onchange_partner_bank(self, cursor, user, ids, partner_bank_id=False):
	return {'value': {}}


    def test_paid(self, cr, uid, ids, *args):
        res = self.move_line_id_payment_get(cr, uid, ids)
        if not res:
            return False
        ok = True
        for id in res:
            cr.execute('select reconcile_id from account_move_line where id=%s', (id,))
            ok = ok and  bool(cr.fetchone()[0])
        return ok

    # Workflow stuff
    #################

    # go from canceled state to draft state
    def action_cancel_draft(self, cr, uid, ids, *args):
	self.write(cr, uid, ids, {'state':'draft'})
	wf_service = netsvc.LocalService("workflow")
	for fee_id in ids:
		wf_service.trg_delete(uid, 'account.fees', fee_id, cr)
		wf_service.trg_create(uid, 'account.fees', fee_id, cr)
	return True

    # return the ids of the move lines which has the same account than the invoice
    # whose id is in ids
    def move_line_id_payment_get(self, cr, uid, ids, *args):
        if not ids: return []
        result = self.move_line_id_payment_gets(cr, uid, ids, *args)
        return result.get(ids[0], [])

    def move_line_id_payment_gets(self, cr, uid, ids, *args):
        res = {}
        if not ids: return res
        cr.execute('SELECT i.id, l.id '\
                   'FROM account_move_line l '\
                   'LEFT JOIN account_fees i ON (i.move_id=l.move_id) '\
                   'WHERE i.id IN %s '\
                   'AND l.account_id=i.account_id',
                   (tuple(ids),))
        for r in cr.fetchall():
            res.setdefault(r[0], [])
            res[r[0]].append( r[1] )
        return res

    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('account.fees.tax')
        for id in ids:
            cr.execute("DELETE FROM account_fees_tax WHERE fees_id=%s AND manual is False", (id,))
            partner = self.browse(cr, uid, id, context=ctx).partner_id
            if partner.lang:
                ctx.update({'lang': partner.lang})
            for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
                ait_obj.create(cr, uid, taxe)
        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.fees').write(cr, uid, ids, {'fees_line':[]}, context=ctx)
        return True


    def confirm_paid(self, cr, uid, ids, context=None):
	if context is None:
		context = {}
	self.write(cr, uid, ids, {'state':'paid'}, context=context)
	return True

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'state':'draft',
            'number':False,
            'move_id':False,
            'move_name':False,
            'internal_number': False,
            'period_id': False,
            'sent': False,
        })
        if 'date_fees' not in default:
            default.update({
                'date_fees':False
            })
        return super(account_honorarios, self).copy(cr, uid, id, default, context)


    def action_move_create(self, cr, uid, ids, context=None):
	"""Creates ballot fees related analytics and financial move lines"""
	ait_obj = self.pool.get('account.fees.tax')
	cur_obj = self.pool.get('res.currency')
	period_obj = self.pool.get('account.period')
	payment_term_obj = self.pool.get('account.payment.term')
	journal_obj = self.pool.get('account.journal')
	move_obj = self.pool.get('account.move')
	if context is None:
		context = {}
	for fee in self.browse(cr, uid, ids, context=context):
		if not fee.journal_id.sequence_id:
			raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this ballot fees.'))
		if not fee.fees_line:
			raise osv.except_osv(_('No Ballot Fees Lines!'), _('Please create some ballot fees lines.'))
		if fee.move_id:
			continue

		ctx = context.copy()
		ctx.update({'lang': fee.partner_id.lang})
		if not fee.date_fees:
			self.write(cr, uid, [fee.id], {'date_fees': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
		company_currency = self.pool['res.company'].browse(cr, uid, fee.company_id.id).currency_id.id
		# create the analytical lines
		# one move line per ballot fees line
		iml = self._get_analytic_lines(cr, uid, fee.id, context=ctx)
		# check if taxes are all computed
		compute_taxes = ait_obj.compute(cr, uid, fee.id, context=ctx)
		self.check_tax_lines(cr, uid, fee, compute_taxes, ait_obj)

		# I disabled the check_total feature
		group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
		group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
		if group_check_total and uid in [x.id for x in group_check_total.users]:
			if (abs(fee.check_total - fee.amount_total) >= (fee.currency_id.rounding/2.0)):
				raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the ballot fees!\nThe encoded total does not match the computed total.'))

		if fee.payment_term:
			total_fixed = total_percent = 0
			for line in fee.payment_term.line_ids:
				if line.value == 'fixed':
					total_fixed += line.value_amount
				if line.value == 'procent':
					total_percent += line.value_amount
			total_fixed = (total_fixed * 100) / (fee.amount_total or 1.0)
			if (total_fixed + total_percent) > 100:
				raise osv.except_osv(_('Error!'), _("Cannot create the ballot fees.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total ballot fees amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

		# one move line per tax line
		iml += ait_obj.move_line_get(cr, uid, fee.id)

		entry_type = 'journal_pur_voucher'

		diff_currency_p = fee.currency_id.id <> company_currency
		# create one move line for the total and possibly adjust the other lines amount
		total = 0
		total_currency = 0
		total, total_currency, iml = self.compute_fees_totals(cr, uid, fee, company_currency, iml, context=ctx)
		acc_id = fee.account_id.id

		name = fee['name'] or 'servicio de honorarios'
		totlines = False
		if fee.payment_term:
			totlines = payment_term_obj.compute(cr,
				uid, fee.payment_term.id, total, fee.date_fees or False, context=ctx)
		if totlines:
			res_amount_currency = total_currency
			i = 0
			ctx.update({'date': fee.date_fees})
			for t in totlines:
				if fee.currency_id.id != company_currency:
					amount_currency = cur_obj.compute(cr, uid, company_currency, fee.currency_id.id, t[1], context=ctx)
				else:
					amount_currency = False

			# last line add the diff
			res_amount_currency -= amount_currency or 0
			i += 1
			if i == len(totlines):
				amount_currency += res_amount_currency

			iml.append({
				'type': 'dest',
				'name': name,
				'price': t[1],
				'account_id': acc_id,
				'date_maturity': t[0],
				'amount_currency': diff_currency_p \
					and amount_currency or False,
				'currency_id': diff_currency_p \
					and fee.currency_id.id or False,
			})
		else:
			iml.append({
				'type': 'dest',
				'name': name,
				'price': total,
				'account_id': acc_id,
				'date_maturity': fee.date_fees or False,
				'amount_currency': diff_currency_p \
					and total_currency or False,
				'currency_id': diff_currency_p \
					and fee.currency_id.id or False,
			})
	
		#Guarda el monto en moneda de la empresa
		monto_nacional = 0
		tax_nacional = 0
		#Guarda el monto de la unidad
		monto_unidad = 0
		tax_unidad = 0
		#Guarda el monto de la divisa de la boleta
		monto_divisa = 0
		tax_divisa = 0
			
		for fees_line in iml:
			if 'type' in fees_line and 'src' in fees_line.get('type'):
				monto_nacional += fees_line['price']
				monto_unidad += fees_line['price_unit']
				if fees_line['amount_currency']:
					monto_divisa += fees_line['amount_currency']
			if 'type' in fees_line and 'tax' in fees_line.get('type'):
				tax_nacional = fees_line['price']
				tax_unidad = fees_line['price_unit']
				if fees_line['amount_currency']:
					tax_divisa = fees_line['amount_currency']
				fees_line['price'] *= -1
			if 'type' in fees_line and 'dest' in fees_line.get('type'):
				fees_line['price'] = (monto_nacional - tax_nacional)*-1
				fees_line['price_unit'] = monto_unidad - tax_unidad
				if monto_divisa:
					fees_line['amount_currency'] = (monto_divisa - tax_divisa)*-1

		date = fee.date_fees or time.strftime('%Y-%m-%d')
		part = self.pool.get("res.partner")._find_accounting_partner(fee.partner_id)
		line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)
		line = self.group_lines(cr, uid, iml, line, fee)
		journal_id = fee.journal_id.id
		journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
		
		if journal.centralisation:
			raise osv.except_osv(_('User Error!'),
				_('You cannot create an ballot fees on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

		line = self.finalize_fees_move_lines(cr, uid, fee, line)

		move = {
			'line_id': line,
			'journal_id': journal_id,
			'date': date,
			'narration': fee.comment,
			'company_id': fee.company_id.id,
		}

		period_id = fee.period_id and fee.period_id.id or False
		ctx.update(company_id=fee.company_id.id, account_period_prefer_normal=True)

		if not period_id:
			period_ids = period_obj.find(cr, uid, fee.date_fees, context=ctx)
			period_id = period_ids and period_ids[0] or False
		if period_id:
			move['period_id'] = period_id
			for i in line:
				i[2]['period_id'] = period_id

		ctx.update(fees=fee)
		move_id = move_obj.create(cr, uid, move, context=ctx)
		new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name

		# make the ballot fees point to that move
		self.write(cr, uid, [fee.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)

		# Pass ballot fees in context in method post: used if you want to get the same
		# account move reference when creating the same ballot fees after a cancelled one:
		move_obj.post(cr, uid, [move_id], context=ctx)

	self._log_event(cr, uid, ids)
	return True


    def fees_validate(self, cr, uid, ids, context=None):
	self.write(cr, uid, ids, {'state':'open'}, context=context)
	return True


    def action_number(self, cr, uid, ids, context=None):
	if context is None:
		context = {}
	#TODO: not correct fix but required a frech values before reading it.
	self.write(cr, uid, ids, {})

	for obj_fee in self.browse(cr, uid, ids, context=context):
		number = obj_fee.number
		move_id = obj_fee.move_id and obj_fee.move_id.id or False

		self.write(cr, uid, ids, {'internal_number': number})

		ref = self._convert_ref(cr, uid, number)

		cr.execute('UPDATE account_move SET ref=%s ' \
			'WHERE id=%s AND (ref is null OR ref = \'\')',
			(ref, move_id))
		cr.execute('UPDATE account_move_line SET ref=%s ' \
			'WHERE move_id=%s AND (ref is null OR ref = \'\')',
			(ref, move_id))
		cr.execute('UPDATE account_analytic_line SET ref=%s ' \
			'FROM account_move_line ' \
			'WHERE account_move_line.move_id = %s ' \
			'AND account_analytic_line.move_id = account_move_line.id',
			(ref, move_id))
	return True


    def action_cancel(self, cr, uid, ids, context=None):
	if context is None:
		context = {}
	account_move_obj = self.pool.get('account.move')
	fees = self.read(cr, uid, ids, ['move_id', 'payment_ids'])
	move_ids = [] # ones that we will need to remove
	for i in fees:
		if i['move_id']:
			move_ids.append(i['move_id'][0])
		if i['payment_ids']:
			account_move_line_obj = self.pool.get('account.move.line')
			pay_ids = account_move_line_obj.browse(cr, uid, i['payment_ids'])
			for move_line in pay_ids:
				if move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids:
					raise osv.except_osv(_('Error!'), _('You cannot cancel an ballot fees which is partially paid. You need to unreconcile related payment entries first.'))

	# First, set the ballot fees as cancelled and detach the move ids
	self.write(cr, uid, ids, {'state':'cancel', 'move_id':False})
	if move_ids:
		# second, invalidate the move(s)
		account_move_obj.button_cancel(cr, uid, move_ids, context=context)
		# delete the move this ballot fees was pointing to
		# Note that the corresponding move_lines and move_reconciles
		# will be automatically deleted too
		account_move_obj.unlink(cr, uid, move_ids, context=context)
	self._log_event(cr, uid, ids, -1.0, 'Cancel Ballot Fees')
	return True


    def action_date_assign(self, cr, uid, ids, *args):
	for fee in self.browse(cr, uid, ids):
		res = self.onchange_payment_term_date_fees(cr, uid, fee.id, fee.payment_term.id, fee.date_fees)
		if res and res['value']:
			self.write(cr, uid, [fee.id], res['value'])
	return True


    def _get_analytic_lines(self, cr, uid, id, context=None):
	if context is None:
		context = {}
	fee = self.browse(cr, uid, id)
	cur_obj = self.pool.get('res.currency')

	company_currency = self.pool['res.company'].browse(cr, uid, fee.company_id.id).currency_id.id
	sign = -1

	iml = self.pool.get('account.fees.line').move_line_get(cr, uid, fee.id, context=context)
	for il in iml:
		if il['account_analytic_id']:
                	if not fee.journal_id.analytic_journal_id:
                	    raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (fee.journal_id.name,))
                	il['analytic_lines'] = [(0,0, {
                	    'name': il['name'],
                	    'date': fee['date_fees'],
                	    'account_id': il['account_analytic_id'],
                	    'unit_amount': il['quantity'],
                	    'amount': cur_obj.compute(cr, uid, fee.currency_id.id, company_currency, il['price'],\
			    	context={'date': fee.date_fees}) * sign,
                	    'product_id': il['product_id'],
                	    'product_uom_id': il['uos_id'],
                	    'general_account_id': il['account_id'],
                	    'journal_id': fee.journal_id.analytic_journal_id.id,
                	})]
	return iml


    def check_tax_lines(self, cr, uid, fee, compute_taxes, ait_obj):
        company_currency = self.pool['res.company'].browse(cr, uid, fee.company_id.id).currency_id
        if not fee.tax_line:
            for tax in compute_taxes.values():
                ait_obj.create(cr, uid, tax)
        else:
            tax_key = []
            for tax in fee.tax_line:
                if tax.manual:
                    continue
                key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id, tax.account_analytic_id.id)
                tax_key.append(key)
                if not key in compute_taxes:
                    raise osv.except_osv(_('Warning!'), _('Global taxes defined, but they are not in ballot fees lines !'))
                base = compute_taxes[key]['base']
                if abs(base - tax.base) > company_currency.rounding:
                    raise osv.except_osv(_('Warning!'), _('Tax base different!\nClick on compute to update the tax base.'))
            for key in compute_taxes:
                if not key in tax_key:
                    raise osv.except_osv(_('Warning!'), _('Taxes are missing!\nClick on compute button.'))


    def compute_fees_totals(self, cr, uid, fee, company_currency, fees_move_lines, context=None):
	if context is None:
		context={}
	total = 0
	total_currency = 0
	cur_obj = self.pool.get('res.currency')
	for i in fees_move_lines:
		if fee.currency_id.id != company_currency:
			context.update({'date': fee.date_fees or time.strftime('%Y-%m-%d')})
			i['currency_id'] = fee.currency_id.id
			i['amount_currency'] = i['price']
			i['price'] = cur_obj.compute(cr, uid, fee.currency_id.id,
				company_currency, i['price'], context=context)
		else:
			i['amount_currency'] = False
			i['currency_id'] = False
			total -= i['price']
			total_currency -= i['amount_currency'] or i['price']
	return total, total_currency, fees_move_lines


    def line_get_convert(self, cr, uid, x, part, date, context=None):
		return {
			'date_maturity': x.get('date_maturity', False),
			'partner_id': part,
			'name': x['name'][:64],
			'date': date,
			'debit': x['price']>0 and x['price'],
			'credit': x['price']<0 and -x['price'],
			'account_id': x['account_id'],
			'analytic_lines': x.get('analytic_lines', []),
			'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
			'currency_id': x.get('currency_id', False),
			'tax_code_id': x.get('tax_code_id', False),
			'tax_amount': x.get('tax_amount', False),
			'quantity': x.get('quantity',1.00),
			'product_id': x.get('product_id', False),
			'product_uom_id': x.get('uos_id', False),
			'analytic_account_id': x.get('account_analytic_id', False),
		}


    def group_lines(self, cr, uid, iml, line, fee):
	"""Merge account move lines (and hence analytic lines) if ballot fees line hashcodes are equals"""

	if fee.journal_id.group_invoice_lines:#OJO CON ESTO ;)
		line2 = {}
		for x, y, l in line:
			tmp = self.fee_line_characteristic_hashcode(fee, l)

	                if tmp in line2:
				am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
				line2[tmp]['debit'] = (am > 0) and am or 0.0
				line2[tmp]['credit'] = (am < 0) and -am or 0.0
				line2[tmp]['tax_amount'] += l['tax_amount']
				line2[tmp]['analytic_lines'] += l['analytic_lines']
			else:
				line2[tmp] = l
		line = []
		for key, val in line2.items():
			line.append((0,0,val))
	return line


    def fee_line_characteristic_hashcode(self, fees, fees_line):
	"""Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""

	return "%s-%s-%s-%s-%s"%(
		fees_line['account_id'],
		fees_line.get('tax_code_id',"False"),
		fees_line.get('product_id',"False"),
		fees_line.get('analytic_account_id',"False"),
		fees_line.get('date_maturity',"False"))


    def finalize_fees_move_lines(self, cr, uid, fees_browse, move_lines):
	"""finalize_invoice_move_lines(cr, uid, fees, move_lines) -> move_lines
	    Hook method to be overridden in additional modules to verify and possibly alter the
	    move lines to be created by an ballot fees, for special cases.
           :param fees_browse: browsable record of the ballot fees that is generating the move lines
           :param move_lines: list of dictionaries with the account.move.lines (as for create())
           :return: the (possibly updated) final move_lines to create for this ballot fees
        """
	return move_lines


    def _log_event(self, cr, uid, ids, factor=1.0, name='Open Ballot Fees'):
	#TODO: implement messages system
	return True


    def _convert_ref(self, cr, uid, ref):
	return (ref or '').replace('/','')

    ###################

"""
    def button_compute(self, cr, uid, ids, context=None, set_total=False):
        self.button_reset_taxes(cr, uid, ids, context)
        for fee in self.browse(cr, uid, ids, context=context):
            if set_total:
                self.pool.get('account.fees').write(cr, uid, [inv.id], {'check_total':feee.amount_total})
        return True


    def list_distinct_taxes(self, cr, uid, ids):
        invoices = self.browse(cr, uid, ids)
        taxes = {}
        for inv in invoices:
            for tax in inv.tax_line:
                if not tax['name'] in taxes:
                    taxes[tax['name']] = {'name': tax['name']}
        return taxes.values()

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        types = {
                'out_invoice': _('Invoice'),
                'in_invoice': _('Supplier Invoice'),
                'out_refund': _('Refund'),
                'in_refund': _('Supplier Refund'),
                }
        return [(r['id'], '%s %s' % (r['number'] or types[r['type']], r['name'] or '')) for r in self.read(cr, uid, ids, ['type', 'number', 'name'], context, load='_classic_write')]

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('number','=',name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def _refund_cleanup_lines(self, cr, uid, lines, context=None):
"""
#        ""Convert records to dict of values suitable for one2many line creation
#            :param list(browse_record) lines: records to convert
#            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
#        ""
"""       clean_lines = []
        for line in lines:
            clean_line = {}
            for field in line._all_columns.keys():
                if line._all_columns[field].column._type == 'many2one':
                    clean_line[field] = line[field].id
                elif line._all_columns[field].column._type not in ['many2many','one2many']:
                    clean_line[field] = line[field]
                elif field == 'invoice_line_tax_id':
                    tax_list = []
                    for tax in line[field]:
                        tax_list.append(tax.id)
                    clean_line[field] = [(6,0, tax_list)]
            clean_lines.append(clean_line)
        return map(lambda x: (0,0,x), clean_lines)

    def _prepare_refund(self, cr, uid, invoice, date=None, period_id=None, description=None, journal_id=None, context=None):
"""
#        ""Prepare the dict of values to create the new refund from the invoice.
#            This method may be overridden to implement custom
#            refund generation (making sure to call super() to establish
#            a clean extension chain).

#            :param integer invoice_id: id of the invoice to refund
#            :param dict invoice: read of the invoice to refund
#            :param string date: refund creation date from the wizard
#            :param integer period_id: force account.period from the wizard
#            :param string description: description of the refund from the wizard
#            :param integer journal_id: account.journal from the wizard
#            :return: dict of value to create() the refund
#        ""
"""        obj_journal = self.pool.get('account.journal')

        type_dict = {
            'out_invoice': 'out_refund', # Customer Invoice
            'in_invoice': 'in_refund',   # Supplier Invoice
            'out_refund': 'out_invoice', # Customer Refund
            'in_refund': 'in_invoice',   # Supplier Refund
        }
        invoice_data = {}
        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id', 'company_id',
                'account_id', 'currency_id', 'payment_term', 'user_id', 'fiscal_position']:
            if invoice._all_columns[field].column._type == 'many2one':
                invoice_data[field] = invoice[field].id
            else:
                invoice_data[field] = invoice[field] if invoice[field] else False

        invoice_lines = self._refund_cleanup_lines(cr, uid, invoice.invoice_line, context=context)

        tax_lines = filter(lambda l: l['manual'], invoice.tax_line)
        tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines, context=context)
        if journal_id:
            refund_journal_ids = [journal_id]
        elif invoice['type'] == 'in_invoice':
            refund_journal_ids = obj_journal.search(cr, uid, [('type','=','purchase_refund')], context=context)
        else:
            refund_journal_ids = obj_journal.search(cr, uid, [('type','=','sale_refund')], context=context)

        if not date:
            date = time.strftime('%Y-%m-%d')
        invoice_data.update({
            'type': type_dict[invoice['type']],
            'date_invoice': date,
            'state': 'draft',
            'number': False,
            'invoice_line': invoice_lines,
            'tax_line': tax_lines,
            'journal_id': refund_journal_ids and refund_journal_ids[0] or False,
        })
        if period_id:
            invoice_data['period_id'] = period_id
        if description:
            invoice_data['name'] = description
        return invoice_data

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None, context=None):
        new_ids = []
        for invoice in self.browse(cr, uid, ids, context=context):
            invoice = self._prepare_refund(cr, uid, invoice,
                                                date=date,
                                                period_id=period_id,
                                                description=description,
                                                journal_id=journal_id,
                                                context=context)
            # create the new invoice
            new_ids.append(self.create(cr, uid, invoice, context=context))

        return new_ids

    def pay_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id, period_id, pay_journal_id, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context=None, name=''):
        if context is None:
            context = {}
        #TODO check if we can use different period for payment and the writeoff line
        assert len(ids)==1, "Can only pay one invoice at a time."
        invoice = self.browse(cr, uid, ids[0], context=context)
        src_account_id = invoice.account_id.id
        # Take the seq as name for move
        types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
        #take the choosen date
        if 'date_p' in context and context['date_p']:
            date=context['date_p']
        else:
            date=time.strftime('%Y-%m-%d')

        # Take the amount in currency and the currency of the payment
        if 'amount_currency' in context and context['amount_currency'] and 'currency_id' in context and context['currency_id']:
            amount_currency = context['amount_currency']
            currency_id = context['currency_id']
        else:
            amount_currency = False
            currency_id = False

        pay_journal = self.pool.get('account.journal').read(cr, uid, pay_journal_id, ['type'], context=context)
        if invoice.type in ('in_invoice', 'out_invoice'):
            if pay_journal['type'] == 'bank':
                entry_type = 'bank_pay_voucher' # Bank payment
            else:
                entry_type = 'pay_voucher' # Cash payment
        else:
            entry_type = 'cont_voucher'
        if invoice.type in ('in_invoice', 'in_refund'):
            ref = invoice.reference
        else:
            ref = self._convert_ref(cr, uid, invoice.number)
        partner = self.pool['res.partner']._find_accounting_partner(invoice.partner_id)
        # Pay attention to the sign for both debit/credit AND amount_currency
        l1 = {
            'debit': direction * pay_amount>0 and direction * pay_amount,
            'credit': direction * pay_amount<0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': partner.id,
            'ref':ref,
            'date': date,
            'currency_id':currency_id,
            'amount_currency':amount_currency and direction * amount_currency or 0.0,
            'company_id': invoice.company_id.id,
        }
        l2 = {
            'debit': direction * pay_amount<0 and - direction * pay_amount,
            'credit': direction * pay_amount>0 and direction * pay_amount,
            'account_id': pay_account_id,
            'partner_id': partner.id,
            'ref':ref,
            'date': date,
            'currency_id':currency_id,
            'amount_currency':amount_currency and - direction * amount_currency or 0.0,
            'company_id': invoice.company_id.id,
        }

        if not name:
            name = invoice.invoice_line and invoice.invoice_line[0].name or invoice.number
        l1['name'] = name
        l2['name'] = name

        lines = [(0, 0, l1), (0, 0, l2)]
        move = {'ref': ref, 'line_id': lines, 'journal_id': pay_journal_id, 'period_id': period_id, 'date': date}
        move_id = self.pool.get('account.move').create(cr, uid, move, context=context)

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        move_ids = [move_id,]
        if invoice.move_id:
            move_ids.append(invoice.move_id.id)
        cr.execute('SELECT id FROM account_move_line '\
                   'WHERE move_id IN %s',
                   ((move_id, invoice.move_id.id),))
        lines = line.browse(cr, uid, map(lambda x: x[0], cr.fetchall()) )
        for l in lines+invoice.payment_ids:
            if l.account_id.id == src_account_id:
                line_ids.append(l.id)
                total += (l.debit or 0.0) - (l.credit or 0.0)

        inv_id, name = self.name_get(cr, uid, [invoice.id], context=context)[0]
        if (not round(total,self.pool.get('decimal.precision').precision_get(cr, uid, 'Account'))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(cr, uid, line_ids, 'manual', writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        else:
            code = invoice.currency_id.symbol
            # TODO: use currency's formatting function
            msg = _("Invoice partially paid: %s%s of %s%s (%s%s remaining).") % \
                    (pay_amount, code, invoice.amount_total, code, total, code)
            self.message_post(cr, uid, [inv_id], body=msg, context=context)
            self.pool.get('account.move.line').reconcile_partial(cr, uid, line_ids, 'manual', context)

        # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {}, context=context)
        return True
"""
account_honorarios()


class account_honorarios_line(osv.osv):

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
    	# CAMBIO PARA QUE FUNCIONE EL ASIENTO CON MONTOS DE IMPUESTO INCLUIDO EN VALOR DE LA LINEA
	res = {}
	cur_obj = self.pool.get('res.currency')
	for line in self.browse(cr, uid, ids):
		res[line.id] = line.price_unit
		if line.fees_id:
			cur = line.fees_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
	return res

    def _price_unit_default(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('check_total', False):
            t = context['check_total']
            for l in context.get('fees_line', {}):
                if isinstance(l, (list, tuple)) and len(l) >= 3 and l[2]:
                    tax_obj = self.pool.get('account.tax')
                    p = l[2].get('price_unit', 0) * (1-l[2].get('discount', 0)/100.0)
                    t = t - (p * l[2].get('quantity'))
                    taxes = l[2].get('fees_line_tax_id')
                    if len(taxes[0]) >= 3 and taxes[0][2]:
                        taxes = tax_obj.browse(cr, uid, list(taxes[0][2]))
                        for tax in tax_obj.compute_all(cr, uid, taxes, p,l[2].get('quantity'), l[2].get('product_id', False), context.get('partner_id', False))['taxes']:
                            t = t - tax['amount']
            return t
        return 0


    _name = "account.fees.line"
    _description = "Ballot Fees Line"
    _columns = {
        'name': fields.text('Description', required=True),
        'origin': fields.char('Source Document', size=256, help="Reference of the document that produced this invoice."),
        'sequence': fields.integer('Sequence', help="Gives the sequence of this line when displaying the ballot fees."),
        'fees_id': fields.many2one('account.fees', 'Ballot Fees Reference', ondelete='cascade', select=True),
        'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null', select=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', select=True),
        'account_id': fields.many2one('account.account', 'Account', required=True,\
		domain=[('type','<>','view'), ('type', '<>', 'closed')],\
		help="The income or expense account related to the selected product."),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
            digits_compute= dp.get_precision('Account'), store=True),
        'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure'), required=True),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
        'fees_line_tax_id': fields.many2many('account.tax', 'account_fees_line_tax', 'fees_line_id', 'tax_id', 'Retencion',\
		domain=[('parent_id','=',False)]),
        'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'company_id': fields.related('fees_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
        'partner_id': fields.related('fees_id','partner_id',type='many2one',relation='res.partner',string='Partner',store=True)
    }


    def _default_account_id(self, cr, uid, context=None):
        # XXX this gets the default account for the user's company,
        # it should get the default account for the invoice's company
        # however, the ballot fees's company does not reach this point
        if context is None:
            context = {}
        prop = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
        return prop and prop.id or False


    _defaults = {
        'quantity': 1,
        'discount': 0.0,
        'price_unit': _price_unit_default,
        'account_id': _default_account_id,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
	if context is None:
		context = {}
	res = super(account_honorarios_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,\
		context=context, toolbar=toolbar, submenu=submenu)
	doc = etree.XML(res['arch'])
	for node in doc.xpath("//field[@name='product_id']"):
		##########################################################
		##########################################################
		##########OJO DE NUEVO, CAMBIAR EN PRODUCTO###############
		############AGREGAR BOLETAS DE HONORARIOS#################
		##########################################################
		node.set('domain', "[('purchase_ok', '=', True)]")
	res['arch'] = etree.tostring(doc)
       
	return res


    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id, 'force_company': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined!'),_("You must first select a partner!") )
        if not product:
	    return {'value': {}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        a = res.property_account_expense.id
        if not a:
            a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

        result.update( {'price_unit': price_unit or res.standard_price,'fees_line_tax_id': tax_id} )
        result['name'] = res.partner_ref

        result['uos_id'] = uom_id or res.uom_id.id
        if res.description:
            result['name'] += '\n'+res.description

        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}

        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if result['uos_id'] and result['uos_id'] != res.uom_id.id:
            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])
            res_final['value']['price_unit'] = new_price
        return res_final

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id})
        warning = {}
        res = self.product_id_change(cr, uid, ids, product, uom, qty, name, partner_id, fposition_id, price_unit, currency_id, context=context)
        if not uom:
            res['value']['price_unit'] = 0.0
        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('The selected unit of measure is not compatible with the unit of measure of the product.')
                }
                res['value'].update({'uos_id': prod.uom_id.id})
            return {'value': res['value'], 'warning': warning}
        return res

    def move_line_get(self, cr, uid, fees_id, context=None):
    	######################################################################
    	######################################################################
	##############Aki calcula impuestos###################################
    	######################################################################
    	######################################################################
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        fee = self.pool.get('account.fees').browse(cr, uid, fees_id, context=context)
        company_currency = self.pool['res.company'].browse(cr, uid, fee.company_id.id).currency_id.id
        for line in fee.fees_line:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            for tax in tax_obj.compute_all(cr, uid, line.fees_line_tax_id, (line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),\
                    line.quantity, line.product_id, fee.partner_id)['taxes']:
                tax_code_id = tax['ref_base_code_id']
                tax_amount = line.price_subtotal * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, fee.currency_id.id, company_currency, tax_amount, context={'date': fee.date_fees})
        return res

    def move_line_get_item(self, cr, uid, line, context=None):
        return {
            'type':'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit':line.price_unit,
            'quantity':line.quantity,
            'price':line.price_subtotal,
            'account_id':line.account_id.id,
            'product_id':line.product_id.id,
            'uos_id':line.uos_id.id,
            'account_analytic_id':line.account_analytic_id.id,
            'taxes':line.fees_line_tax_id,
        }
	
    #
    # Set the tax field according to the account and the fiscal position
    #
    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, fposition_id, account_id):
        if not account_id:
            return {}
        unique_tax_ids = []
        fpos = fposition_id and self.pool.get('account.fiscal.position').browse(cr, uid, fposition_id) or False
        account = self.pool.get('account.account').browse(cr, uid, account_id)
        if not product_id:
            taxes = account.tax_ids
            unique_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
        else:
            product_change_result = self.product_id_change(cr, uid, ids, product_id, False,
                partner_id=partner_id, fposition_id=fposition_id,
                company_id=account.company_id.id)
            if product_change_result and 'value' in product_change_result and 'fees_line_tax_id' in product_change_result['value']:
                unique_tax_ids = product_change_result['value']['fees_line_tax_id']
        return {'value':{'fees_line_tax_id': unique_tax_ids}}

account_honorarios_line()

class account_honorarios_tax(osv.osv):
    _name = "account.fees.tax"
    _description = "Ballot Fees Tax"

    def _count_factor(self, cr, uid, ids, name, args, context=None):
        res = {}
        for fees_tax in self.browse(cr, uid, ids, context=context):
            res[fees_tax.id] = {
                'factor_base': 1.0,
                'factor_tax': 1.0,
            }
            if fees_tax.amount <> 0.0:
                factor_tax = fees_tax.tax_amount / fees_tax.amount
                res[fees_tax.id]['factor_tax'] = factor_tax

            if fees_tax.base <> 0.0:
                factor_base = fees_tax.base_amount / fees_tax.base
                res[fees_tax.id]['factor_base'] = factor_base

        return res

    _columns = {
        'fees_id':fields.many2one('account.fees', 'Ballot Fees Line', ondelete='cascade', select=True),
        'name':fields.char('Tax Description', size=64, required=True),
        'account_id':fields.many2one('account.account', 'Tax Account', required=True,\
		domain=[('type', '<>', 'closed')]),
        'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic account'),
        'base':fields.float('Base', digits_compute=dp.get_precision('Account')),
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'manual':fields.boolean('Manual'),
        'sequence':fields.integer('Sequence', help="Gives the sequence order when displaying a list of ballot fees tax."),
        'base_code_id':fields.many2one('account.tax.code', 'Base Code', help="The account basis of the tax declaration."),
        'base_amount':fields.float('Base Code Amount', digits_compute=dp.get_precision('Account')),
        'tax_code_id':fields.many2one('account.tax.code', 'Tax Code', help="The tax basis of the tax declaration."),
        'tax_amount':fields.float('Tax Code Amount', digits_compute=dp.get_precision('Account')),
        'company_id':fields.related('account_id', 'company_id', type='many2one',
		relation='res.company', string='Company', store=True, readonly=True),
        'factor_base':fields.function(_count_factor, string='Multipication factor for Base code', type='float', multi="all"),
        'factor_tax':fields.function(_count_factor, string='Multipication factor Tax code', type='float', multi="all")
    }

    def base_change(self, cr, uid, ids, base, currency_id=False, company_id=False, date_fees=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency = False
        factor = 1
        if ids:
            factor = self.read(cr, uid, ids[0], ['factor_base'])['factor_base']
        if company_id:
            company_currency = company_obj.read(cr, uid, [company_id], ['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            base = cur_obj.compute(cr, uid, currency_id, company_currency, base*factor, context={'date': date_fees or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'base_amount':base}}

    def amount_change(self, cr, uid, ids, amount, currency_id=False, company_id=False, date_fees=False):
        cur_obj = self.pool.get('res.currency')
        company_obj = self.pool.get('res.company')
        company_currency = False
        factor = 1
        if ids:
            factor = self.read(cr, uid, ids[0], ['factor_tax'])['factor_tax']
        if company_id:
            company_currency = company_obj.read(cr, uid, [company_id], ['currency_id'])[0]['currency_id'][0]
        if currency_id and company_currency:
            amount = cur_obj.compute(cr, uid, currency_id, company_currency, amount*factor, context={'date': date_fees or time.strftime('%Y-%m-%d')}, round=False)
        return {'value': {'tax_amount': amount}}

    _order = 'sequence'
    _defaults = {
        'manual': 1,
        'base_amount': 0.0,
        'tax_amount': 0.0,
    }

    def compute(self, cr, uid, fees_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        fee = self.pool.get('account.fees').browse(cr, uid, fees_id, context=context)
        cur = fee.currency_id
        company_currency = self.pool['res.company'].browse(cr, uid, fee.company_id.id).currency_id.id
        for line in fee.fees_line:
            for tax in tax_obj.compute_all(cr, uid, line.fees_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, fee.partner_id)['taxes']:
                val={}
                val['fees_id'] = fee.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])
                val['base_code_id'] = tax['ref_base_code_id']
                val['tax_code_id'] = tax['ref_tax_code_id']
                val['base_amount'] = cur_obj.compute(cr, uid, fee.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'],\
			context={'date': fee.date_fees or time.strftime('%Y-%m-%d')}, round=False)
                val['tax_amount'] = cur_obj.compute(cr, uid, fee.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'],\
			context={'date': fee.date_fees or time.strftime('%Y-%m-%d')}, round=False)
                val['account_id'] = tax['account_paid_id'] or line.account_id.id
                val['account_analytic_id'] = tax['account_analytic_paid_id']

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

    def move_line_get(self, cr, uid, fees_id):
        res = []
        cr.execute('SELECT * FROM account_fees_tax WHERE fees_id=%s', (fees_id,))
        for t in cr.dictfetchall():
            if not t['amount'] \
                    and not t['tax_code_id'] \
                    and not t['tax_amount']:
                continue
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['amount'],
                'quantity': 1,
                'price': t['amount'] or 0.0,
                'account_id': t['account_id'],
                'tax_code_id': t['tax_code_id'],
                'tax_amount': t['tax_amount'],
                'account_analytic_id': t['account_analytic_id'],
            })
        return res
account_honorarios_tax()

class res_partner(osv.osv):
    """ Inherits partner and adds ballot fees information in the partner form """

    _inherit = 'res.partner'
    _columns = {
        'fees_ids': fields.one2many('account.fees.line', 'partner_id', 'Ballot Fees', readonly=True),
    }

    def _find_accounting_partner(self, partner):
        '''
        Find the partner for which the accounting entries will be created
        '''
        # FIXME: after 7.0, to replace by function field partner.commercial_partner_id

        #if the chosen partner is not a company and has a parent company, use the parent for the journal entries
        #because you want to ballot fees 'Agrolait, accounting department' but the journal items are for 'Agrolait'
        while not partner.is_company and partner.parent_id:
            partner = partner.parent_id
        return partner

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({'fees_ids' : []})
        return super(res_partner, self).copy(cr, uid, id, default, context)


class mail_compose_message(osv.Model):
	_inherit = 'mail.compose.message'

	def send_mail(self, cr, uid, ids, context=None):
		context = context or {}
		if context.get('default_model') == 'account.fees' and context.get('default_res_id') and context.get('mark_fees_as_sent'):
			context = dict(context, mail_post_autofollow=True)
			self.pool.get('account.fees').write(cr, uid, [context['default_res_id']], {'sent': True}, context=context)
		return super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)

