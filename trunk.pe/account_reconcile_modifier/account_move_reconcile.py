# -*- coding: utf-8 -*-
##############################################################################
#
# Author: OpenDrive Ltda
# Copyright (c) 2014 Opendrive Ltda
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

class account_move_reconcile_inherit(osv.osv):
	_inherit = 'account.move.reconcile'

	_columns = {
		'comment':fields.text('Comment'),
		'company_id':fields.many2one('res.company', 'Company', required=True),
	}

	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid,\
						'account.move.reconcile', context=c),
	}
account_move_reconcile_inherit()

