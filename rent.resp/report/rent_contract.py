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

import time, datetime
from collections import defaultdict
from openerp import pooler
from report import report_sxw
import logging
_logger = logging.getLogger(__name__)

class rent_contract(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(rent_contract, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'getmoves': self.getMoves,
			
		})

	""" Todos los Movimientos analiticos con sus centros de costos y tiendas  """
	def getMoves(self, shop):
		return true


report_sxw.report_sxw('report.rent_contract', 'rent.order',\
			'stihl_reports/report/rent_contract.rml', parser=rent_contract, header=False)