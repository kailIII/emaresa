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
_logger = logging.getLogger(__name__)
import requests

#Llamado a cliente para webservice
from suds.client import Client
from suds import WebFault

wsdl = 'http://200.72.31.165:9766/as/services/IntegracionOpenERPLegacyEstadosClientes?wsdl'
try:
	r = requests.get(wsdl)
	r.raise_for_status()
except:
	_logger.warning('Web Service no Accesible.')
else:
	_logger.info( '%s disponible para utilizar'%r.url)
	client = Client(wsdl)


class account_move_fields(osv.osv):
	_inherit = 'account.move'

	def set_ref(self, cr, uid, ids, cause , context=None):
		nombre = self.pool.get('l10n_cl_emaresa_protest_check').browse(cr,uid,cause, context=context).name
		return {'value': {'ref': nombre} }
		
	def post(self, cr, uid, ids, context=None):
		res = super(account_move_fields, self).post(cr, uid, ids, context=context)
		self.lock(cr, uid, ids, context=context)
		return res

	def lock(self, cr, uid, ids, context=None):
		partner_pool = self.pool.get('res.partner')
		move_line_pool = self.pool.get('account.move.line')
		user_obj = self.pool.get('res.users').browse(cr, uid, uid)

		for move in self.browse(cr, uid, ids):
			if move.journal_id.code in ['466', '651', '680', '920', '921', '922', '925',\
				'926', '927', '930', '931', '932', '933', '934', '935']:
				line_ids = move_line_pool.search(cr, uid, [('move_id','=',move.id)])
				for line in move_line_pool.browse(cr, uid, line_ids):
					if line.debit > 0 and line.credit == 0:
						client_obj = partner_pool.browse(cr, uid, line.partner_id.id)

						if client_obj.customer:
							lock_vals = {
								'lock_unlock': 'lock',
								'to_date': None,
								'registry_date': move.date,
								'users_id': uid,
								'partner_id': client_obj.id,
								'description': 'INGRESO A '+move.journal_id.name+'.'
							}

							sale_warn = 'block'

							if lock_vals['description']:
								sale_warn_msg = 'CLIENTE BLOQUEADO POR: '+lock_vals['description']
							self.pool.get('res.partner').write(cr, uid, client_obj.id,\
								{'lock_unlock' : lock_vals['lock_unlock'], 'to_date': lock_vals['to_date'],\
								'sale_warn': sale_warn, 'sale_warn_msg': sale_warn_msg})
							estado = 'BL'
							motivo = lock_vals['description']

							self.pool.get('res.partner.lock_registry').create(cr, uid, lock_vals, context=context)
						
							if user_obj.company_id.id != 4:
							# Comunicacion con el web service
								rut = client_obj.vat
								rut = rut[2:-1]
								centrocosto = user_obj.codecc or '930'
								if client:
									client.service.opActualizaEstadoCliente(rut,estado,motivo,centrocosto)
								else:
									_logger.warning("Error al conectar al webservice")
							# Fin Web Service
							break
		return True

	def _check_number(self, cr, uid, ids, name, args, context=None):
		""" Complete the check number for protest check.
		@return: Dictionary of values
		"""

		res = {}
		for move in self.browse(cr, uid, ids, context=context):
			for line in move.line_id:
				res[move.id] = line.name
				break
		return res

	def _get_lines(self, cr, uid, ids, context=None):
		return self.pool.get('account.move.line').search(cr, uid, [('move_id', 'in', ids)], context=context)

	_columns = {
		'analytic_account_id':fields.many2one('account.analytic.account','Centro de Costo'),
		'protest_cause':fields.many2one('l10n_cl_emaresa_protest_check','Causas de Protesto'),
		'check_number':fields.function(_check_number, type='char', size=15, string="Check Number",
					store={
						'account.move': (lambda *ids: ids[3], ['line_id'], 10),
						'account.move.line': (_get_lines, ['name'], 10)
					})
	}
account_move_fields()

