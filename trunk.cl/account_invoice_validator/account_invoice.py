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
 
class account_invoice_validator(osv.osv):
	_inherit = 'account.invoice'
	
	def invoice_validator(self, cr, uid, ids, context=None):
		if not context:
			context = {}

		for invoice in self.browse(cr, uid, ids, context):
			if not invoice.type in ('in_invoice','in_refund'):
				continue
			domain = []
			domain.append( ('id','!=',invoice.id) )
			domain.append( ('partner_id','=',invoice.partner_id.id) )
			domain.append( ('type','=',invoice.type) )
			domain.append( ('reference', '=', invoice.reference) )
			domain.append( ('journal_id', '=', invoice.journal_id.id) )
			domain.append( ('state','in', ('draft','open','paid')) )
			invoice_ids = self.search(cr, uid, domain, context=context)
 			if len(invoice_ids) >= 1:
				text = []
				for invoice in self.browse(cr, uid, invoice_ids, context):
					text.append( _('Empresa: %s\nReferecia de Factura: %s\nPeriodo: %s') % ( invoice.partner_id.name, invoice.reference, invoice.period_id.name ) )
				text = '\n\n'.join( text )
				raise osv.except_osv( _('Error de Validacion'), _('Su factura de proveedores contiene informacion duplicada con:\n\n%s') % text)
		return {}


	def write(self, cr, uid, ids, vals, context=None):
	        result = super(account_invoice_validator, self).write(cr, uid, ids, vals, context)
		if vals.get('state') == 'open' or vals.get('state') == 'draft':
			for invoice in self.browse(cr, uid, ids, context):
				if not invoice.type in ('in_invoice','in_refund'):
					continue
				domain = []
				domain.append( ('partner_id','=',invoice.partner_id.id) )
				domain.append( ('type','=',invoice.type) )
				domain.append( ('reference', '=', invoice.reference) )
				domain.append( ('journal_id', '=', invoice.journal_id.id) )
				domain.append( ('state','in', ('draft','open','paid')) )
				invoice_ids = self.search(cr, uid, domain, context=context)
				if len(invoice_ids) > 1:
					text = []
					for invoice in self.browse(cr, uid, invoice_ids, context):
						text.append( _('Empresa: %s\nReferecia de Factura: %s\nPeriodo: %s') % ( invoice.partner_id.name, invoice.reference, invoice.period_id.name ) )
					text = '\n\n'.join( text )
					raise osv.except_osv( _('Error de Validacion'), _('Su factura de proveedores contiene informacion duplicada:\n\n%s') % text)
		return result

account_invoice_validator()
