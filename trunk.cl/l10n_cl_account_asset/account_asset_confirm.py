# -*- encoding: utf-8 -*-
#
# OpenERP Correccion Monetaria
# Copyright (C) 2013 OpenDrive Ltda.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import datetime
from osv import osv, fields

class account_asset(osv.osv_memory):
	_name =  'account.asset.asset.confirm'

	def confirmar(self, cr, uid, ids, context=None):
		if context is None:
			context = {}

		for asset_id in context['active_ids']:
			if self.pool.get('account.asset.asset').browse(cr, uid, asset_id).state != 'open':
				self.pool.get('account.asset.asset').validate(cr, uid, asset_id, context)

		return True
	
account_asset()

