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

from openerp.osv import osv, fields
from openerp.tools.translate import _

class rent_invoice(osv.osv):
	_inherit = 'account.invoice.line'

	def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
		if context is None:
			context = {}
		company_id = company_id if company_id != None else context.get('company_id',False)
		context = dict(context)
		context.update({'company_id': company_id})
		warning = {}
		res = self.product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context=context)
		if not uom:
			res['value']['price_unit'] = 0.0
		if product and uom:
			prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
			prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
			if prod.uom_id.category_id.id != prod_uom.category_id.id:
				if type != 'out_invoice' and not prod.can_be_rent:
					warning = {
						'title': _('Warning!'),
						'message': _('The selected unit of measure is not compatible with the unit of measure of the product.')
					}
					res['value'].update({'uos_id': prod.uom_id.id})
					return {'value': res['value'], 'warning': warning}
		return res
rent_invoice()

