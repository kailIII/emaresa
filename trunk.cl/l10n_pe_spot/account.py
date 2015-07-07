# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import osv, fields
from openerp.tools.translate import _
import time
import netsvc

class account_transfer(osv.osv):
    
    STATE_SELECTION = [
        ('draft','Draft'),
        ('confirm','Confirm'),
        ('done','Done'),
        ('cancel','Cancel'),
        ('spot','Spot Transfer'),
    ]

    #def _get_type(self, cr, uid, context=None):
        #res = super(account_transfer,self)._get_type(cr, uid, context=context)
        #res.append(('spot','Spot Transfer'))
        #return res
    
    _inherit = 'account.transfer'
    _columns = {
        'type': fields.selection(STATE_SELECTION,'Type', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'is_spot' : fields.boolean('Is SPOT', readonly=True, help="This record is automatically generated by spot module, e.g. detractions"),
    }
    _defaults = {
        'is_spot': False,
    }

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
		'spot_operation_type' : fields.selection(lambda s,c,u,context={}:s.pool.get('base.element').get_selection(c,u,'PE.SPOT.ANEXO_05',context=c),
                                     'SPOT Operation Type',help="kind of operation subjected to SPOT (detractions) - SUNAT"),
    }

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'spot_operation_type' : fields.selection(lambda s,c,u,context={}:s.pool.get('base.element').get_selection(c,u,'PE.SPOT.ANEXO_05',context=c),
                                     'SPOT Operation Type',help="kind of operation subjected to SPOT (detractions) - SUNAT"),
    }

    def transfer_spot_get(self, cr, uid, invoice, spot_amount, context=None):
        cur_obj = self.pool.get('res.currency')
        transfer_obj = self.pool.get('account.transfer')
        amount = cur_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.spot_bank_journal_id.currency.id or invoice.company_id.currency_id.id,
                                     spot_amount, context={'date': invoice.date_invoice})
        value = transfer_obj.onchange_journal(cr, uid, [invoice.id], invoice.company_id.spot_bank_journal_id.id, 
                            invoice.partner_id.property_spot_journal.id,time.strftime('%Y-%m-%d'), 1.0, amount)['value']
        return {'company_id': invoice.company_id.id,
                'origin': invoice.name,
                'src_journal_id': invoice.company_id.spot_bank_journal_id.id,
                'src_amount': amount,
                'dst_journal_id': invoice.partner_id.property_spot_journal.id,
                'dst_partner_id': invoice.partner_id.id,
                'dst_amount': value['dst_amount'],
                'exchange_rate': value['exchange_rate'],
                'invoice_id': invoice.id,
                'is_spot': True,
            }
        
        
    def reset_transfer_spot(self, cr, uid, invoice, spot_amount,context=None):
        res = 0
        if invoice.type not in ['in_invoice','out_invoice']:
            return res
        transfer_obj = self.pool.get('account.transfer')
        transfer_ids = transfer_obj.search(cr, uid, [('invoice_id','=',invoice.id),('is_spot','=',True)], context=context)
        transfer_obj.unlink(cr, uid, transfer_ids, context=context)
        if spot_amount:
            if not invoice.company_id.spot_bank_journal_id:
                raise osv.except_osv(_('Error'),_('SPOT bank journal not found. Please fill this in the configuration menu, account sheet, bank & Cash settings or in the company form.'))
            if not invoice.partner_id.property_spot_journal.id:
                raise osv.except_osv(_('Error'),_('Detractions Journal to pay not found. Please fill this in the partner form.'))
            res = transfer_obj.create(cr,uid,self.transfer_spot_get(cr, uid, invoice, spot_amount, context=context),context=context)
        return res
    
    def reset_transfer_bank_spot(self, cr, uid, invoice, spot_amount,context=None):
        res = 0
        if invoice.type not in ['in_invoice','out_invoice']:
            return res
        cur_obj = self.pool.get('res.currency')
        transfer_obj = self.pool.get('account.transfer')
        if invoice.type in ('out_invoice'):
            transfer_ids = transfer_obj.search(cr, uid, [('invoice_id','=',invoice.id),('is_spot','=',True)], context=context)
            transfer_obj.unlink(cr, uid, transfer_ids, context=context)
        if spot_amount:
            if not invoice.company_id.spot_bank_journal_id:
                raise osv.except_osv(_('Error'),_('SPOT bank journal not found. Please fill this in the account configuration form or company form.'))
            if not invoice.company_id.detraction_journal_id:
                raise osv.except_osv(_('Error'),_('The bank detractions Journal to pay detractions not found. Please fill this in the company form.'))
            amount = cur_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.spot_bank_journal_id.currency.id or invoice.company_id.currency_id.id,
                                     spot_amount, context={'date': invoice.date_invoice})
            value = transfer_obj.onchange_journal(cr, uid, [invoice.id], invoice.company_id.spot_bank_journal_id.id, 
                            invoice.company_id.detraction_journal_id.id,time.strftime('%Y-%m-%d'), 1.0, amount)['value']
            res = transfer_obj.create(cr,uid,{
                            'company_id': invoice.company_id.id,
                            'origin': invoice.number,
                            'src_journal_id': invoice.company_id.spot_bank_journal_id.id,
                            'src_amount': amount,
                            'dst_journal_id': invoice.company_id.detraction_journal_id.id,
                            'dst_partner_id': invoice.partner_id.id,
                            'dst_amount': value['dst_amount'],
                            'exchange_rate': value['exchange_rate'],
                            'invoice_id': invoice.id,
                            'is_spot': True,
                        },context=context)
        return res
    
        
    def compute_spot_amount(self, cr, uid, invoice, context=None):
        if invoice.type not in ['in_invoice','out_invoice']:
            return 0.0
        element_obj = self.pool.get('base.element')
        line_obj = self.pool.get('account.invoice.line')
        cur_obj = self.pool.get('res.currency')
        if not invoice.spot_operation_type:
            if invoice.journal_id.spot_operation_type:
                self.write(cr, uid, [invoice.id], {'spot_operation_type':invoice.journal_id.spot_operation_type}, context=context)
        spot_amount = 0.0
        for line in invoice.invoice_line:
            spot_percent = 0.0
            new_spot_product_type = ''
            if not line.spot_product_type:
                if not line.product_id:
                    continue
                elif not line.product_id.spot_product_type:
                    if line.product_id.categ_id.spot_product_type:
                        new_spot_product_type = line.product_id.categ_id.spot_product_type
                        spot_percent = element_obj.get_percent(cr,uid,'PE.SPOT.ANEXO_04',new_spot_product_type)
                else:
                    new_spot_product_type = line.product_id.spot_product_type
                    spot_percent = element_obj.get_percent(cr,uid,'PE.SPOT.ANEXO_04',line.product_id.spot_product_type)
            else:
                spot_percent = element_obj.get_percent(cr,uid,'PE.SPOT.ANEXO_04',line.spot_product_type)
            if new_spot_product_type:
                line_obj.write(cr,uid,[line.id],{'spot_product_type':new_spot_product_type},context=context)
            if spot_percent:
                spot_amount += cur_obj.round(cr, uid, invoice.currency_id, line.price_subtotal * spot_percent)
        return spot_amount
        
    def compute_spot_pay(self, cr, uid, inv, context=None):
        cur_obj = self.pool.get('res.currency')
        spot_pay = 0.0
        for line in inv.payment_ids:
            if line.journal_id.id == inv.company_id.detraction_journal_id.id:
                if (inv.currency_id.id == (line.journal_id.currency.id or inv.company_id.currency_id.id)):
                    spot_pay += line.credit or -line.debit
                else:
                    if (inv.currency_id == (line.currency_id.id or inv.company_id.currency_id.id)):
                        spot_pay += line.amount_currency or line.credit or -line.debit 
                    else:
                        spot_pay += cur_obj.compute(cr, uid, line.journal_id.currency.id or inv.company_id.currency_id.id, inv.currency_id.id,
                                                    line.credit or -line.debit, context={'date': inv.date_invoice})
        return spot_pay
        
    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.type not in ('in_invoice'): 
                continue
            spot_amount = self.compute_spot_amount(cr, uid, invoice, context=context)
            self.reset_transfer_spot(cr, uid, invoice, spot_amount, context=context)
        return super(account_invoice,self).button_reset_taxes(cr, uid, ids, context=context)
        
    def spot_voucher_get(self, cr, uid, invoice, trans, context=None):
        val = {}
        val['date'] = time.strftime('%Y-%m-%d')
        val['type'] = 'payment'
        val['company_id'] = trans.company_id.id
        val['reference'] = trans.name + str(invoice['number'] and (' - ' + invoice['number']) or '')
        val['partner_id'] = self.pool.get('res.partner')._find_accounting_partner(invoice.partner_id).id
        val['amount'] = trans.dst_amount
        val['journal_id'] = trans.dst_journal_id.id
        val['account_id'] = trans.dst_journal_id.default_debit_account_id.id
        val['payment_rate'] = trans.dst_journal_id.currency.id and trans.company_id.currency_id.id <> trans.dst_journal_id.currency.id  and trans.exchange_inv or 1.0
        val['payment_rate_currency_id'] = trans.dst_journal_id.currency.id or trans.company_id.currency_id.id
        
        val['line_dr_ids'] = [(0,0,{})]
        val['line_dr_ids'][0][2]['account_analytic_id'] = trans.account_analytic_id and trans.account_analytic_id.id or 0
        val['line_dr_ids'][0][2]['currency_id'] = trans.dst_journal_id.currency.id or trans.company_id.currency_id.id
        val['line_dr_ids'][0][2]['amount'] = trans.dst_amount
        val['line_dr_ids'][0][2]['name'] = trans.origin
        move_line_ids = [x.id for x in invoice.move_id.line_id if x.account_id.id == invoice.account_id.id]
        val['line_dr_ids'][0][2]['move_line_id'] = move_line_ids and move_line_ids[0] or 0
        val['line_dr_ids'][0][2]['amount_unreconciled'] = invoice.account_id.id
        val['line_dr_ids'][0][2]['amount_original'] = invoice.account_id.id
        val['line_dr_ids'][0][2]['account_id'] = invoice.account_id.id
        val['line_dr_ids'][0][2]['type'] = 'dr'
        val['line_dr_ids'][0][2]['date_due'] = invoice.date_due
        val['line_dr_ids'][0][2]['date_original'] = invoice.date_invoice
        return val
    
    def confirm_spot_transfer(self, cr, uid, invoice, context=None):
        if invoice.type not in ('in_invoice'): 
            return False
        context = context or {}
        voucher_obj = self.pool.get("account.voucher")
        transfer_obj = self.pool.get("account.transfer")
        wf_service = netsvc.LocalService("workflow")
        for trans in invoice.transfer_ids:
            if not trans.is_spot or trans.state != 'draft':
                continue
            transfer_obj.write(cr, uid, [trans.id], {'origin': invoice.name}, context=context)
            ctx = context.copy()
            ctx['close_after_process'] = True
            ctx['invoice_type'] = invoice.type
            ctx['invoice_id'] = invoice.id,
            ctx['type'] = 'payment'
            voucher_id = voucher_obj.create(cr, uid, self.spot_voucher_get(cr, uid, invoice, trans, context=context), context=ctx)
            wf_service.trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
            wf_service.trg_validate(uid, 'account.transfer', trans.id, 'transfer_confirm', cr)
            self.pool.get('account.transfer').write(cr, uid, [trans.id], {'origin':invoice['number']}, context=ctx)
        return True
    
    def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
        cur_obj = self.pool.get('res.currency')
        if inv.type in ('in_invoice'):
            if not inv.transfer_ids:
                spot_amount = self.compute_spot_amount(cr, uid, inv)
                self.reset_transfer_spot(cr, uid, inv, spot_amount)
            else:
                spot_amount = self.compute_spot_amount(cr, uid, inv)
                transfer_amount = 0.0
                for transfer in inv.transfer_ids:
                    if transfer.is_spot and transfer.state not in ('cancel'):
                        transfer_amount += cur_obj.compute(cr, uid, transfer.src_journal_id.currency.id or transfer.company_id.currency_id.id,
                                        inv.currency_id.id, transfer.src_amount, context={'date': inv.date_invoice})   
                if abs(transfer_amount - spot_amount) > 0.01:
                    raise osv.except_osv(_('Warning!'), _('SPOT amount transfered (detraction) different!\nClick on compute to update the spot amount transfers.'))
        return super(account_invoice,self).check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)    

    def invoice_validate(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('in_invoice'):
                self.confirm_spot_transfer(cr, uid, inv, context=context)
        return super(account_invoice,self).invoice_validate(cr, uid, ids, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for invoice in self.browse(cr, uid, ids, context=context):
            for transfer in invoice.transfer_ids:
                if transfer.is_spot:
                    wf_service.trg_validate(uid, 'account.transfer', transfer.id, 'transfer_cancel', cr)
        return super(account_invoice,self).action_cancel(cr, uid, ids, context=context)

    def action_cancel_draft(self, cr, uid, ids, *args):
        for i in self.browse(cr,uid,ids):
            for transfer in i.transfer_ids:
                if transfer.is_spot:
                    netsvc.LocalService("workflow").trg_validate(uid, 'account.transfer', transfer.id, 'transfer_draft', cr)
                    if i.type in ('out_invoice',):
                        self.pool.get('account.transfer').unlink(cr, uid, [transfer.id])
        return super(account_invoice,self).action_cancel_draft(cr, uid, ids, *args)

    def confirm_paid(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('out_invoice'):
                spot_amount = self.compute_spot_amount(cr, uid, inv, context=context)
                spot_pay_amount = self.compute_spot_pay(cr, uid, inv, context=context)
                if abs(spot_pay_amount - spot_amount) > 0.01:
                    self.reset_transfer_bank_spot(cr, uid, inv, spot_amount,context=context)
        return super(account_invoice,self).confirm_paid(cr, uid, ids, context=context)

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'spot_product_type' : fields.selection(lambda s,c,u,context={}:s.pool.get('base.element').get_selection(c,u,'PE.SPOT.ANEXO_04',context=c),
                                     'SPOT Product Type',help="kind of goods and services subjected to SPOT (detractions) - SUNAT"),
    }