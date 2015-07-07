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
############################################################################### -*- coding: UTF-8 -*-

import datetime
from report import report_sxw
from report.report_sxw import rml_parse


class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		self.cuenta = (context['cuenta']).encode('ascii','ignore')
		self.compania = str(context['compania_id'])

		self.localcontext.update({
			'periodos': self.periodos,
			'cuentas_analiticas': self.cuentas_analiticas,
			'monto' : self.monto,
			'monto_anterior' : self.monto_anterior,
	        }) 

	def periodos(self):
        	cr = self.cr
	        uid = self.uid
        	cr.execute("select name,date_start from account_period where name like '%2014%' and account_period.company_id='"+ self.compania +"' order by code")
        	periodos = cr.dictfetchall()
        	return periodos
	
	def cuentas_analiticas(self):
   		cr = self.cr
	        uid = self.uid
	        cr.execute("select ca.name from account_analytic_account ca where ca.company_id='"+ self.compania +"' group by ca.name order by ca.name")
	        cuentas_analiticas = cr.dictfetchall()
		return cuentas_analiticas

	def monto(self,periodo,cuenta_analitica):

   		cr = self.cr
	        uid = self.uid	
		montos = 0
		cuenta_contable = (self.cuenta).encode('ascii','ignore')

		sql ='select sum(al.amount)  from account_analytic_line al ' \
			' inner join account_analytic_account ca on al.account_id=ca.id ' \
			' inner join account_account cc on al.general_account_id=cc.id ' \
			' inner join account_move_line mv on al.move_id=mv.id ' \
			' inner join account_period p on mv.period_id=p.id ' \
			" where cc.name='"+(cuenta_contable).encode('ascii','ignore')+"' and ca.name='"+(cuenta_analitica).encode('ascii','ignore')+"' and p.name='"+(periodo).encode('ascii','ignore')+"'"\
			" and ca.company_id='"+ self.compania +"' group by cc.name order by cc.name"
		cr.execute(sql)
		for suma in cr.fetchall():
			montos = suma
		return montos

	def monto_anterior(self,periodo,cuenta_analitica):
   		cr = self.cr
	       	uid = self.uid	
		montos_anterior = 0
		cuenta_contable = (self.cuenta).encode('ascii','ignore')

		sql_fecha="select date_start from account_period where name='"+(periodo).encode('ascii','ignore')+"' and  account_period.company_id='"+ self.compania +"'"

		cr.execute(sql_fecha)

		for f in cr.fetchall():
			fecha = f

		sql ='select sum(al.amount)  from account_analytic_line al ' \
			'inner join account_analytic_account ca on al.account_id=ca.id ' \
			'inner join account_account cc on al.general_account_id=cc.id ' \
			'inner join account_move_line mv on al.move_id=mv.id ' \
			'inner join account_period p on mv.period_id=p.id ' \
			"where cc.name='"+(cuenta_contable).encode('ascii','ignore')+"' and ca.name='"+(cuenta_analitica).encode('ascii','ignore')+"' and p.date_start=(date('"+fecha[0]+"') - interval '1 year') "\
			" and ca.company_id='"+ self.compania +"' group by cc.name order by cc.name"
		cr.execute(sql)
	
		for suma in cr.fetchall():
			montos_anterior = suma
		return montos_anterior




