# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
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

from openerp.osv import fields, osv

class account_invoice(osv.osv):
	_inherit = 'account.invoice'
	
	def action_number(self, cr, uid, ids, *args):
		result = super(account_invoice, self).action_number(cr, uid, ids, *args)
		for inv in self.browse(cr, uid, ids):
			self.pool.get('account.invoice.line').asset_create_tributario(cr, uid, inv.invoice_line)
		return result

	def line_get_convert(self, cr, uid, x, part, date, context=None):
		res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
		res['asset_id'] = x.get('asset_id', False)
		return res
account_invoice()

class account_invoice_line(osv.osv):
	_inherit = 'account.invoice.line'
	
	_columns = {
		'asset_category_tributario_id':fields.many2one('account.asset.category', 'Asset Tributario Category')
	}
	
	def asset_create_tributario(self, cr, uid, lines, context=None):
		context = context or {}
		asset_obj = self.pool.get('account.asset.asset')
		for line in lines:
			if line.asset_category_tributario_id:
				vals = {
					'name': line.name,
					'code': line.invoice_id.number or False,
					'purchase_value': line.price_subtotal,
					'category_id': line.asset_category_tributario_id.id,
					'period_id': line.invoice_id.period_id.id,
					'partner_id': line.invoice_id.partner_id.id,
					'company_id': line.invoice_id.company_id.id,
					'currency_id': line.invoice_id.currency_id.id,
					'purchase_date' : line.invoice_id.date_invoice,
				}
				changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
				vals.update(changed_vals['value'])
				asset_id = asset_obj.create(cr, uid, vals, context=context)
				if line.asset_category_tributario_id.open_asset:
					asset_obj.validate(cr, uid, [asset_id], context=context)
		return True
account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

