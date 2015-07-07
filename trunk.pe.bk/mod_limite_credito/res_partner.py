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

class res_partner_modLimiteCredito(osv.osv):
	_inherit = 'res.partner'

	def _get_credit_limit_function(self, cr, uid, ids, name, arg, context=None):
		res={}

		for partner in self.browse( cr, uid, ids ,context=None):
			res[partner.id] = partner['credit_limit'] or 0.0
		
		return res

	_columns = {
		'credit_limit_view':fields.function(_get_credit_limit_function, type='float', string='Limite de Credito'),
	}
res_partner_modLimiteCredito()
