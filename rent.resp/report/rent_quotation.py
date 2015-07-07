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

from report import report_sxw
from report.report_sxw import rml_parse
import re

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.item = 0

		self.localcontext.update({
			'get_partner_username': self.get_partner_username,
			'price_type': self.price_type,
			'get_vat': self.get_vat,
			'get_item': self.get_item,
		})

	def price_type(self, price):
		if price == 'day':
			return 'Dia x Equipo'
		elif price == 'week':
			return 'Semana x Equipo'
		elif price == 'month':
			return 'Mes x Equipo'
		else:
			return ''


	def get_partner_username(self, child_ids):
		print "entro a get_partner_username"
		name = "--"
		if child_ids:
			for user in child_ids:
				name = child_ids[0].name
				if user:
					for tags in user.category_id:
						if tags:
							if tags.name == "CONTACTO":
								name = user.name
								return name
							else:
								name = child_ids[0].name
						else:
							name = child_ids[0].name
				else:
					name = child_ids[0].name

		return name

	def get_vat(self, vat, ref):
		print "entro a get_vat"
		if vat:
			return vat[2:]
		elif ref:
			return ref
		return ''

	def get_item(self):
		print "entro a get_item"
		self.item += 1
		return self.item

report_sxw.report_sxw('report.rent_order_rml', 'rent.order', 'rent/report/rent_quotation.rml', parser=Parser, header=False)
