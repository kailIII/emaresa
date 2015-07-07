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
 
class stock_picking_fields(osv.osv):
	_inherit = 'stock.picking'

	_columns = {
		'number':fields.char('Number Office Guide', size=20),
		'proof_type':fields.selection([('invoice', 'Invoice'),\
			('ballot_sale','Ballot Sale'),\
			('credit_note','Credit Note'),\
			('debit_note','Debit Note'),\
			('other','Other')],\
			'Proof Type'),
		'proof_number':fields.char('Proof Number', size=20),
		'sale':fields.boolean('Sale'),
		'sale_sac':fields.boolean('Sale Sac'),
		'purchase':fields.boolean('Purchase'),
		'despatch':fields.boolean('Despatch'),
		'refound':fields.boolean('Refound'),
		'between_establishments':fields.boolean('Between Establishments'),
		'for_processing':fields.boolean('For Processing'),
		'pick_processed':fields.boolean('Pick Processed'),
		'itinerant_issuer':fields.boolean('Itinerant Issuer'),
		'primary_zone':fields.boolean('Primary Zone'),
		'import':fields.boolean('Import'),
		'export':fields.boolean('Export')
	}
stock_picking_fields()

class stock_picking_out_fields(osv.osv):
	_inherit = 'stock.picking.out'

	_columns = {
		'number':fields.char('Number Office Guide', size=20),
		'proof_type':fields.selection([('invoice', 'Invoice'),\
			('ballot_sale','Ballot Sale'),\
			('credit_note','Credit Note'),\
			('debit_note','Debit Note'),\
			('other','Other')],\
			'Proof Type'),
		'proof_number':fields.char('Proof Number', size=20),
		'sale':fields.boolean('Sale'),
		'sale_sac':fields.boolean('Sale Sac'),
		'purchase':fields.boolean('Purchase'),
		'despatch':fields.boolean('Despatch'),
		'refound':fields.boolean('Refound'),
		'between_establishments':fields.boolean('Between Establishments'),
		'for_processing':fields.boolean('For Processing'),
		'pick_processed':fields.boolean('Pick Processed'),
		'itinerant_issuer':fields.boolean('Itinerant Issuer'),
		'primary_zone':fields.boolean('Primary Zone'),
		'import':fields.boolean('Import'),
		'export':fields.boolean('Export')
	}
stock_picking_out_fields()
