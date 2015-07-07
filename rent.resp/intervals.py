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

class InvoiceInterval(osv.osv):
	"""
	This object represents a invoice interval the user can used when invoicing rent orders.

	In this object, we define the name of the interval, and the name of the python method called.
	If you want to add support for a specific interval, just creates one of this object, inherit rent.order
	and add your custom method with this signature :

	method(self, cr, uid, order, context=None)

	Where order is the result of a browse() on the current order. This method must returns a list of the created
	invoices ids, or raise an exception.
	"""

	_name = 'rent.interval'

	_columns = {
		'name':fields.char('Name', size=150, required=True, translate=True),
		'method':fields.char('Method', size=255, required=True),
		'not_allowed_duration_unities':fields.many2many('product.uom', 'rent_interval_not_allowed_durations',
			'interval_id', 'duration_id', string='Duration not allowed with this interval !'),
	}
InvoiceInterval()
