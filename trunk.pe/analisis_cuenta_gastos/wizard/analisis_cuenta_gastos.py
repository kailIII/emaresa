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
import logging

_logger = logging.getLogger('analisis_cuenta_gastos')

class wizard_analisis_cuenta_gastos(osv.osv_memory):
	_name="reporte_analisis_cuenta_gastos"

	_columns = {
		'cuentas':fields.many2one('account.account', 'Cuentas', required=False),
		'compania_id':fields.many2one('res.company', 'Companias', required=False),
		'report_xml_id':fields.many2one('ir.actions.report.xml', 'Report Name',\
			domain="[('report_type','=','aeroo'),('model','=','account')]",\
			context="{'default_report_type': 'aeroo', 'default_model': 'account'}", required=True),
	}

	_defaults = {
		'report_xml_id': lambda self,cr,uid,c:\
			self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=','report_analisis_cuenta_gastos')], context=c)[0]
	}

	def generate_report(self, cr, uid, ids, context=None):
		wizard = self.browse(cr, uid, ids[0])
		context['cuenta'] = wizard.cuentas.name
		context['compania_id'] = wizard.compania_id.id
		report_name = wizard.report_xml_id.report_name

		result = {
			'type' : 'ir.actions.report.xml',
			'context' : context,
			'report_name': report_name
		}

	        return result

wizard_analisis_cuenta_gastos()

