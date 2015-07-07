# -*- encoding: utf-8 -*-
#
# Lock / Unlock Client
# Copyright (C) 2013 David Acevedo Toledo (Fedoro) <dacevedo@opendrive.cl>
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

from osv import osv, fields
import datetime

class res_partner_lock_registry(osv.osv):
	_name = 'res.partner.lock_registry'
	_order = 'id desc'

	_columns = {
		'lock_unlock':fields.selection([('unlock','Unlock'),('lock','Lock')], 'State', required=True),
		'to_date':fields.date('To Date'),
		'registry_date':fields.date('Registry Date', required=True),
		'users_id':fields.many2one('res.users','User', required=True),
		'partner_id':fields.many2one('res.partner', 'Partner', required=True),
		'description':fields.text('Lock/Unlock Reason')
	}
res_partner_lock_registry()

class res_partner(osv.osv):
	_inherit = 'res.partner'

	_columns = {
		'to_date':fields.date('To Date'),
		'lock_unlock':fields.selection([('unlock','Unlock'),('lock','Lock')], 'Lock/Unlock'),
		'lock_registry':fields.one2many('res.partner.lock_registry', 'partner_id', 'Lock Registry'),
	}

	_defaults = {
		'lock_unlock': 'unlock',
	}
res_partner()
