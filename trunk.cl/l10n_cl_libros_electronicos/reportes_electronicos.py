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
import base64, cStringIO
from openerp.tools.translate import _


class reportes_electronicos(osv.osv_memory):
	_name = 'reportes.electronicos'

	def _get_period(self, cr, uid, context=None):
		periods = self.pool.get('account.period').find(cr, uid)
		return periods and periods[0] or False

	_columns = {   
		'name':fields.char('Name', size=25, readonly=True),
		'company_id':fields.many2one('res.company', 'Company', required=True),
		'period_id':fields.many2one('account.period', 'Periods', required=True, help="select the period of ebooks"),
		'type':fields.selection([('purchases_book', 'Purchases'),('sales_book', 'Sales')], 'Type of Report'),
		'data':fields.binary('File', readonly=True),
		'state':fields.selection([('choose','choose'),('get','get')], 'state', required=True),
	}

	_defaults = {
		'state': 'choose',
		'name': 'libro.txt',
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr,\
				uid, 'reportes.electronicos', context=c),
		'type': 'sales_book',
		'period_id': _get_period
	}

	def formatRut(self, rut):
		if rut:
			return rut[2:-1]+'-'+rut[-1:]

	def formatLang(self, amount, digits=None):
		return int(amount)

	def create_report(self, cr, uid, ids, context=None):
		tipo_doc = {}
		buf = cStringIO.StringIO()
		wizard = self.browse(cr, uid, ids)[0]

		wizard.name = str(wizard.type)+'.txt'
		month, year = str(wizard.period_id.name).split('/')

		####### LIBRO DE VENTAS #######
		if wizard.type == 'sales_book':
			################### FILA A ###################
			buf.write('A;VENTA;MENSUAL;83162400-0;'+year+'-'+month+';TOTAL;;;\n')


			################### FILAS B ###################
			#Valores Afectos VENTAS
			cr.execute("select j.code_sii, count(i.id), sum(amount_untaxed), sum(amount_tax),\
				sum(amount_total) from account_invoice as i inner join account_journal as j on (i.journal_id = j.id)\
				where j.type_tax = 'A' and (i.type = 'out_invoice' or i.type = 'out_refund')\
				and (state = 'paid' or state = 'open') and period_id = %s\
				group by j.code_sii;",(wizard.period_id.id,))

			for code_sii, cantidad, neto, iva, total in cr.fetchall():
				if code_sii and cantidad and neto and iva and total:
					buf.write('B;'+code_sii+';;'+str(cantidad)+';;0;'+str(self.formatLang(neto, digits=0))+';;'+\
						str(self.formatLang(iva, digits=0))+';0;0;;0;0;0;;0;;0;;0;;;'+\
						str(self.formatLang(total, digits=0))+';0;;;;;;;;;;0;0;0;;0;\n')
				
			#Valores Excentos VENTAS
			cr.execute("select j.code_sii, count(i.id), sum(amount_untaxed), sum(amount_total) from account_invoice as i\
				inner join account_journal as j ON (i.journal_id = j.id)\
				where j.type_tax = 'E' and (i.type = 'out_invoice' or i.type = 'out_refund')\
				and (state = 'paid' or state = 'open') and period_id = %s\
				group by j.code_sii;",(wizard.period_id.id,))

			for code_sii, cantidad, neto, total in cr.fetchall():
				if code_sii and cantidad and neto and total:
					buf.write('B;'+code_sii+';;'+str(cantidad)+';;0;'+str(self.formatLang(neto, digits=0))+';;0'+\
						';0;0;;0;0;0;;0;;0;;0;;;'+str(self.formatLang(total, digits=0))+';0;;;;;;;;;;0;0;0;;0;\n')

			################### FILAS C ###################
			invoice_ids = self.pool.get('account.invoice').search(cr, uid,\
				['|',('type','=','out_refund'),('type','=','out_invoice'),\
				('period_id','=',wizard.period_id.id),('state','in',['paid','open'])])
			invoice_objs = self.pool.get('account.invoice').browse(cr, uid, invoice_ids)
			catidad = len(invoice_ids)
	
			for inv in invoice_objs:
				name = (inv.partner_id.name).encode('ascii','ignore')
				if len(name) > 50:
					name = name[:50]

				if inv.journal_id.type_tax == 'A':
					buf.write('C;'+str(inv.journal_id.code_sii)+';'+str(inv.number)+';;;;19;;;;'+str(inv.date_invoice)+\
			';;'+str(self.formatRut(inv.partner_id.vat))+';'+name+';;;0;'+str(self.formatLang(inv.amount_untaxed, digits=0))+\
			';'+str(self.formatLang(inv.amount_tax, digits=0))+';0;0;;;0;0;0;;;'+str(self.formatLang(inv.amount_total, digits=0))+\
			';0;;;;;;;;;;0;;0;\n')
				else:
					buf.write('C;'+str(inv.journal_id.code_sii)+';'+str(inv.number)+';;;;19;;;;'+str(inv.date_invoice)+\
			';;'+str(self.formatRut(inv.partner_id.vat))+';'+name+';;;0;'+str(self.formatLang(inv.amount_untaxed, digits=0))+\
			';0;0;0;;;0;0;0;;;'+str(self.formatLang(inv.amount_total, digits=0))+';0;;;;;;;;;;0;;0;\n')

			out = base64.encodestring(buf.getvalue())
			buf.close()

			self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': wizard.name}, context=context)

		####### LIBRO DE COMPRAS #######
		elif wizard.type == 'purchases_book':
			################### FILA A ###################
			buf.write('A;COMPRA;MENSUAL;83162400-0;'+year+'-'+month+';TOTAL;;;\n')

			################### FILAS B ###################
			#Valores Afectos COMPRA
			cr.execute("select j.code_sii, count(i.id), sum(amount_untaxed), sum(amount_tax),\
				sum(amount_total) from account_invoice as i inner join account_journal as j on (i.journal_id = j.id)\
				where j.type_tax = 'A' and (i.type = 'in_invoice' or i.type = 'in_refund')\
				and (state = 'paid' or state = 'open') and period_id = %s\
				group by j.code_sii;",(wizard.period_id.id,))

			for code_sii, cantidad, neto, iva, total in cr.fetchall():
				if code_sii and cantidad and neto and iva and total:
					buf.write('B;'+code_sii+';;'+str(cantidad)+';;0;'+str(self.formatLang(neto, digits=0))+';;'+\
					str(self.formatLang(iva, digits=0))+';0;0;;0;0;0;;0;;0;;0;;;'+\
					str(self.formatLang(total, digits=0))+';0;;;;;;;;;;0;0;0;;0;\n')
				
			#Valores Excentos COMPRA
			cr.execute("select j.code_sii, count(i.id), sum(amount_untaxed), sum(amount_total) from account_invoice as i\
				inner join account_journal as j ON (i.journal_id = j.id)\
				where j.type_tax = 'E' and (i.type = 'in_invoice' or i.type = 'in_refund')\
				and (state = 'paid' or state = 'open') and period_id = %s\
				group by j.code_sii;",(wizard.period_id.id,))

			for code_sii, cantidad, neto, total in cr.fetchall():
				if code_sii and cantidad and neto and total:
					buf.write('B;'+code_sii+';;'+str(cantidad)+';;0;'+str(self.formatLang(neto, digits=0))+';;0'+\
						';0;0;;0;0;0;;0;;0;;0;;;'+str(self.formatLang(total, digits=0))+';0;;;;;;;;;;0;0;0;;0;\n')

			################### FILAS C ###################
			invoice_ids = self.pool.get('account.invoice').search(cr, uid,\
				['|',('type','=','in_refund'),('type','=','in_invoice'),\
				('journal_id.code','not in',['908', '909', '910', '911', '912', '913', '956', '701']),\
				('period_id','=',wizard.period_id.id),('state','in',['paid','open'])], context=context)
			invoice_objs = self.pool.get('account.invoice').browse(cr, uid, invoice_ids)

			for inv in invoice_objs:
				name = (inv.partner_id.name).encode('ascii','ignore')
				if len(name) > 50:
					name = name[:50]

				if inv.journal_id.type_tax == 'A':
					buf.write('C;'+str(inv.journal_id.code_sii)+';'+str(inv.reference)+';;;;19;;;;'+str(inv.date_invoice)+\
			';;'+str(self.formatRut(inv.partner_id.vat))+';'+name+';;;0;'+str(self.formatLang(inv.amount_untaxed, digits=0))+\
			';'+str(self.formatLang(inv.amount_tax, digits=0))+';0;0;;;0;0;0;;;'+str(self.formatLang(inv.amount_total, digits=0))+\
			';0;;;;;;;;;;0;;0;\n')
				else:
					buf.write('C;'+str(inv.journal_id.code_sii)+';'+str(inv.reference)+';;;;19;;;;'+str(inv.date_invoice)+\
			';;'+str(self.formatRut(inv.partner_id.vat))+';'+name+';;;0;'+str(self.formatLang(inv.amount_untaxed, digits=0))+\
			';0;0;0;;;0;0;0;;;'+str(self.formatLang(inv.amount_total, digits=0))+';0;;;;;;;;;;0;;0;\n')

			out = base64.encodestring(buf.getvalue())
			buf.close()

			self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': wizard.name}, context=context)

		return {
			'type': 'ir.actions.act_window',
			'res_model': 'reportes.electronicos',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wizard.id,
			'views': [(False, 'form')],
			'target': 'new'
		}
reportes_electronicos()
