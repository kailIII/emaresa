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
import datetime,osv
from report import report_sxw
from report.report_sxw import rml_parse
import logging
_logger = logging.getLogger(__name__)

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		self.fiscalyear = str(context['fiscalyear_id'])
		self.compania = str(context['compania_id'])
		self.disponible = 0
		self.apertura()
		
		self.saldo  = 0 
		self.lista = []

		self.localcontext.update({
			'periodos': self.periodos,
			'cuentas': self.cuentas,
			'monto' : self.monto,
			'saldo_periodo' : self.saldo_periodo,
			'disponible_periodo' : self.disponible_periodo,
			'monto_cuenta' : self.monto_cuenta,
	        }) 

	def apertura(self):
		cr = self.cr
		uid = self.uid
		sql = """
			select  (sum(debit) - sum(credit))
				from account_move_line aml
				inner join account_account cuenta on aml.account_id=cuenta.id
				inner join account_period periodo on aml.period_id=periodo.id
				inner join account_journal diario on aml.journal_id=diario.id
				inner join account_move asiento on aml.move_id=asiento.id
					where aml.company_id="""+self.compania+""" and periodo.id = (select min(id) from account_period where fiscalyear_id="""+self.fiscalyear+""" and company_id=3)
			
			and aml.move_id in ( 
					select move_id from account_move_line where account_id in 
					(
						select id from account_account where flujo_caja=True
					)
			) and (cuenta.flujo_caja=False or cuenta.flujo_caja is null) and cuenta.categoria is not null
		"""
		cr.execute(sql)
		for suma in cr.fetchall():
			saldos = suma
		if not saldos[0]:
			self.disponible += 0
		else:
			self.disponible += int(int(saldos[0]))
		return True


	def periodos(self):
        	cr = self.cr
	        uid = self.uid
        	cr.execute("select name from account_period where fiscalyear_id="+self.fiscalyear+" and name like '%/%' order by code")
        	periodos = cr.dictfetchall()
        	return periodos
		
	def titulos(self):
        	cr = self.cr
	        uid = self.uid
        	cr.execute('select name from account_period')
        	periodos = cr.dictfetchall()
        	return titulos

	def cuentas(self):
   		cr = self.cr
        	uid = self.uid
        	cr.execute("""
						select  cuenta.categoria
						from account_move_line aml
						inner join account_account cuenta on aml.account_id=cuenta.id
						inner join account_period periodo on aml.period_id=periodo.id
						inner join account_journal diario on aml.journal_id=diario.id
						inner join account_move asiento on aml.move_id=asiento.id
						where aml.company_id=3 
						and aml.move_id in ( 
							select move_id from account_move_line where account_id in 
							(
								select id from account_account where flujo_caja=True
							)
						) and (cuenta.flujo_caja is null or cuenta.flujo_caja=False) and cuenta.categoria is not null
						group by cuenta.categoria
						order by cuenta.categoria
			""")
        	cuentas = cr.dictfetchall()
		return cuentas

		


	def saldo_periodo(self,periodo):
		cr = self.cr
		uid = self.uid
		sql = """
			select  (sum(debit) - sum(credit))
				from account_move_line aml
				inner join account_account cuenta on aml.account_id=cuenta.id
				inner join account_period periodo on aml.period_id=periodo.id
				inner join account_journal diario on aml.journal_id=diario.id
				inner join account_move asiento on aml.move_id=asiento.id
					where aml.company_id="""+self.compania+""" and periodo.id = (select max(id)-1 from account_period where name='"""+periodo+"""'  and company_id=3)
			and aml.move_id in ( 
					select move_id from account_move_line where account_id in 
					(
						select id from account_account where flujo_caja=True
					)
			) and (cuenta.flujo_caja=False or cuenta.flujo_caja is null) and cuenta.categoria is not null
		"""
		cr.execute(sql)
		
		for suma in cr.fetchall():
			saldos = suma
		if not saldos[0]:
			self.saldo += 0
		else:
			self.saldo += int(saldos[0])
		return int(self.saldo)

	def disponible_periodo(self,periodo):

		cr = self.cr
		uid = self.uid
		sql = """   
				select  (sum(debit) - sum(credit))
					from account_move_line aml
					inner join account_account cuenta on aml.account_id=cuenta.id
					inner join account_period periodo on aml.period_id=periodo.id
					inner join account_journal diario on aml.journal_id=diario.id
					inner join account_move asiento on aml.move_id=asiento.id
					where 	aml.company_id="""+self.compania+""" and periodo.name='"""+periodo+"""' 
						and aml.move_id in ( 
						select move_id from account_move_line where account_id in 
						(
							select id from account_account where flujo_caja=True
						)
					) and (cuenta.flujo_caja is null or cuenta.flujo_caja=False) and cuenta.categoria is not null
		"""
		cr.execute(sql)
		
		for suma in cr.fetchall():
			saldos = suma

		if not saldos[0]:
			self.disponible += 0
		else:
			self.disponible += int(saldos[0])

		return int(self.disponible)

	def monto_cuenta(self,cuenta):
		cr = self.cr
		uid = self.uid
		montos = 0
		sql = """
			select  (sum(debit) - sum(credit))
				from account_move_line aml
				inner join account_account cuenta on aml.account_id=cuenta.id
				inner join account_period periodo on aml.period_id=periodo.id
				inner join account_journal diario on aml.journal_id=diario.id
				inner join account_move asiento on aml.move_id=asiento.id
				where aml.company_id="""+self.compania+""" and periodo.fiscalyear_id="""+self.fiscalyear+""" 
				and cuenta.categoria='"""+cuenta+"""' 
				and aml.move_id in ( 
					select move_id from account_move_line where account_id in 
					(
						select id from account_account where flujo_caja=True
					)
			) and (cuenta.flujo_caja=False or cuenta.flujo_caja is null) and cuenta.categoria is not null
		"""
		cr.execute(sql)
		for suma in cr.fetchall():
			montos = suma
		return montos

	def monto(self,periodo,cuenta):
   		cr = self.cr
        	uid = self.uid	
		montos = 0
		sql = """   
				select  (sum(debit) - sum(credit))
					from account_move_line aml
					inner join account_account cuenta on aml.account_id=cuenta.id
					inner join account_period periodo on aml.period_id=periodo.id
					inner join account_journal diario on aml.journal_id=diario.id
					inner join account_move asiento on aml.move_id=asiento.id
					where 	aml.company_id="""+self.compania+""" and periodo.name='"""+periodo+"""' 
					and cuenta.categoria='"""+cuenta+"""' 
					and aml.move_id in ( 
						select move_id from account_move_line where account_id in 
						(
							select id from account_account where flujo_caja=True
						)
					) and (cuenta.flujo_caja is null or cuenta.flujo_caja=False) and cuenta.categoria is not null
					group by cuenta.categoria		
		"""
		cr.execute(sql)
		for suma in cr.fetchall():
			montos = suma
		return montos

