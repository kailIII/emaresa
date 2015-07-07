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
		'automatic_locking':fields.boolean('Atomatic Locking')
	}

	_defaults = {
		'lock_unlock': 'unlock',
		'automatic_locking': True
	}
res_partner()
