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
import datetime
from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		self.fiscalyear = str(context['fiscalyear_id'])
		self.compania = str(context['compania_id'])
		
		self.localcontext.update({
			'periodos': self.periodos,
			'cuentas': self.cuentas,
			'monto' : self.monto,
			'saldo' : self.saldo,
			'monto_periodo' : self.monto_periodo,
			'monto_cuenta' : self.monto_cuenta,
	        }) 

	def periodos(self):
        	cr = self.cr
	        uid = self.uid
        	cr.execute("select name from account_period where fiscalyear_id="+self.fiscalyear+" order by code")
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
										select id from account_account 
										where code in ( '110101','110102','110322','110345','110355','110356','110357','110361','110701','212801') and cuenta.flujo_caja=True
									)
				) and cuenta.code not in ( '110101','110102','110322','110345','110355','110356','110357','110361','110701','212801') and cuenta.categoria is not null
				order by cuenta.secuencia
			""")
        	cuentas = cr.dictfetchall()
		return cuentas

	def monto_periodo(self,periodo):
   		cr = self.cr
	        uid = self.uid	
		monto_periodo = 0
		sql = 'select sum(amount) from account_bank_statement_line ' \
        		'inner join account_bank_statement on account_bank_statement_line.statement_id=account_bank_statement.id ' \
                'inner join account_account on account_bank_statement_line.account_id=account_account.id ' \
                'inner join account_period on account_bank_statement.period_id=account_period.id ' \
				"where account_period.name='"+periodo+"' and account_account.flujo_caja=True "\
				'group by account_period.name'			

		cr.execute(sql)

		for suma in cr.fetchall():
			if suma=='None':
				monto_periodo = 0
			else:
				monto_periodo = suma
		return monto_periodo

	def monto_cuenta(self,cuenta):
   		cr = self.cr
        	uid = self.uid	
		monto_cuenta = 0
		sql = 'select sum(amount) from account_bank_statement_line ' \
        		'inner join account_bank_statement on account_bank_statement_line.statement_id=account_bank_statement.id ' \
                	'inner join account_account on account_bank_statement_line.account_id=account_account.id ' \
                	'inner join account_period on account_bank_statement.period_id=account_period.id ' \
	               	'inner join account_account_type on account_account_type.id=account_account.user_type ' \
			" where account_account.name='"+cuenta+"'" \
			' group by account_account.name'

		cr.execute(sql)
		for suma in cr.fetchall():
			if suma=='None':
				monto_cuenta = 0
			else:
				monto_cuenta = suma
		return monto_cuenta
		
	def saldo(self,periodo):
   		cr = self.cr
        	uid = self.uid	
		saldos = 0
		sql = """
      
				select  sum(debit-credit)
				from account_move_line aml
				inner join account_account cuenta on aml.account_id=cuenta.id
				inner join account_period periodo on aml.period_id=periodo.id
				inner join account_journal diario on aml.journal_id=diario.id
				inner join account_move asiento on aml.move_id=asiento.id
				where aml.company_id=3 and periodo.name='"""+periodo+"""'
				and aml.move_id in ( 
									select move_id from account_move_line where account_id in 
									(
										select id from account_account 
										where code in ( '110101','110102','110322','110345','110355','110356','110357','110361','110701','212801')
									)
				) and cuenta.code in ( '110101','110102','110322','110345','110355','110356','110357','110361','110701','212801') and cuenta.flujo_caja=True
				group by periodo.name				
		"""
		cr.execute(sql)
		for suma in cr.fetchall():
			saldos = suma
		return saldos


	def monto(self,periodo,cuenta):
   		cr = self.cr
        	uid = self.uid	
		montos = 0
		sql = """
      
				select  sum(debit-credit)
				from account_move_line aml
				inner join account_account cuenta on aml.account_id=cuenta.id
				inner join account_period periodo on aml.period_id=periodo.id
				inner join account_journal diario on aml.journal_id=diario.id
				inner join account_move asiento on aml.move_id=asiento.id
				where aml.company_id=3 and periodo.name='"""+periodo+"""' and cuenta.categoria='"""+cuenta+"""'
				and aml.move_id in ( 
									select move_id from account_move_line where account_id in 
									(
										select id from account_account 
										where code in ( '110101','110102','110322','110345','110355','110356','110357','110361','110701','212801') and flujo_caja=True
									)
				) and cuenta.code not in ( '110101','110102','110322','110345','110355','110356','110357','110361','110701','212801') and cuenta.categoria is not null
				group by periodo.name,cuenta.categoria,cuenta.secuencia			
		"""
		cr.execute(sql)
		for suma in cr.fetchall():
			montos = suma
		return montos

