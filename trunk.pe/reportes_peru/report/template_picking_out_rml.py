# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

import datetime
from report import report_sxw
from report.report_sxw import rml_parse
import re

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		#Obtenemos id del formulario a imprimir
		#self.formulario = uid
		
		self.localcontext.update({
			'get_vat':self.get_vat,
			'mark': self.mark,
		})
	
	def get_vat(self,vat,ref):
		new_vat = ""
		if vat:
			aux = re.findall(r'\d+', vat)
			if aux:
				new_vat = aux[0]
		elif ref:
			new_vat = ref
		else:
			new_vat = ""
		return new_vat

	
	def mark(self, record):
		if record:
			return 'X'
		else:
			return ''

report_sxw.report_sxw('report.stock_picking_out_report_rml', 'stock.picking.out', 
			'reportes_peru/report/stock_picking_out_report.rml', parser=Parser, header=False)