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
import time

class asset_asset_modifier(osv.osv):
	_inherit = 'account.asset.asset'

	def _get_assets(self, cr, uid, ids, context=None):
		return self.pool.get('account.asset.asset').search(cr, uid, [('category_id', 'in', ids)], context=context)

	_columns = {
		'activation_date':fields.date('Activation Date'),
		'derecognised_date':fields.date('Derecognised Date'),
		'accounting_type':fields.related('category_id', 'accounting_type', string='Accounting Type', type='selection',
					selection=[('tributario','Tributario'),('ifrs','IFRS')],
						store={
							'account.asset.asset': (lambda *a: a[3], ['category_id'], 10),
							'account.asset.category': (_get_assets, ['accounting_type'], 20)
						})
	}
asset_asset_modifier()

