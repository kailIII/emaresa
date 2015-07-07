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

import time
from openerp.report import report_sxw

class Parser( report_sxw.rml_parse ):
	def __init__(self,cr,uid,name,context):
		super(Parser,self).__init__(cr,uid,name,context=context)
		self.localcontext.update({
			'formatRut': self.formatRut,
			'time': time,
			'_periodos_v': self._periodos_v,
			'corto_dat_v': self.corto_dat_v,
			'get__v': self._get__v,
			'nuevo':self.nuevo,
			'detalle':self.detalle,
			'subtotales':self.subtotales,
			'totales':self.totales
		})
	def formatRut(self, rut):
		if rut:
			return rut[2:-7]+'.'+rut[-7:-4]+'.'+rut[-4:-1]+'-'+rut[-1:]
		return ''
	
	def _periodos_v(self, period_list):
		aux_=0
		feci=0
		fecf=0
		for period_id in period_list:
			if aux_==0:			
				self.cr.execute("select name from account_period where id=" + str(period_id) + "")	
				for record in self.cr.fetchall():
					feci= record[0]		
			aux_=aux_+1
		self.cr.execute("select name from account_period where id=" + str(period_id) + "")	
		for record in self.cr.fetchall():			
			fecf=record[0]					
		return 'Desde ' + feci + ' Hasta ' + fecf
		
	def corto_dat_v(self,arg1,largo):	
		if len(arg1)>largo:
			descripcion=arg1[:largo-1]
		else:
			descripcion=arg1
		return descripcion				
		
	def _get__v(self,co,pe,si,ty):        
	
		d = []
		
#		arrInfAgrupado={}
		
		#arrInfAgrupado["mundo"]="hola"
		Lds=''
		Lds_=''
		cc=0	
		#cl=0	
		tpOo= ""
		aeOo = 0
		aeS=0
		txS=0
		unS=0  
		toS=0 
		cl=0 
		sum_ae=0
		sum_tx=0
		sum_un=0
		sum_to=0
		
		d.append({'auxiliar':'t',})							
		
		for p in pe:           
			Lds = Lds + str(p) + ","				
			
		while cc<len(Lds)-1:				
			Lds_= Lds_ + Lds[cc]
			cc=cc + 1
		

		sql = """SELECT ai.number
		,date_invoice
		,rp.vat
		, rp.name
		, aj.code
		, ai.amount_untaxed
		,	ai.amount_tax
		, ai.amount_total
		,   (
			select 
			CASE WHEN sum(ait.base_amount) is null 
			then 0 else sum(ait.base_amount) 
			end as a 
			from account_invoice_tax ait 
			where UPPER(ait.name) like UPPER('%exento%') 
			and ait.invoice_id = ai.id
		) base_amount
		,aj.name 	
		FROM   public.account_invoice ai
		,   public.account_journal aj
		,   public.res_partner rp 
		WHERE ai.state not in ('draft', 'cancel') 
		and  ai.partner_id = rp.id 
		AND  aj.id = ai.journal_id 
		and aj.code between '200' and '299' 
		and  ai.period_id in ("""+"".join(map(str, Lds_))+""") 
		and 	ai.company_id = """+ str(co[0])+ """ 
		order by aj.name, ai.number"""
		print(sql)
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			
			
#			aux = [{
#										'number': record[0], 
#										'x_tipo_doc': "",
#										'date_invoice': record[1],
#										'rut': record[2],
#										'cliente': record[3],
#										'afe_exe':self.formatLang(record[8], digits=0),
#										'cc_amount_tax': self.formatLang(record[6], digits=0),
#										'cc_amount_untaxed': self.formatLang(record[5], digits=0),
#										'cc_amount_total': self.formatLang(record[7], digits=0),
#										'auxiliar':'d'
#										}]
#			if len(arrInfAgrupado)>0:
#				arrInfAgrupado[record[9]].append(aux)
#			else:
#				arrInfAgrupado[record[9]]=aux
			
			nmOo = record[0]
			dtOo = record[1]
			rtOo = record[2]
			clOo = record[3]		
			tpOo = ""
			aeOo = record[8]
			
			if record[4]=="201":
				tpOo= "FN"
			elif record[4]=="202":
				tpOo= "FE"
			elif record[4]=="203":
				tpOo= "BV"	
			elif record[4]=="211" or record[4]=="212":
				tpOo= "EX"				
			elif record[4]=="213":
				tpOo= "EEX"
			elif record[4]=="221":
				tpOo= "ND"	
			elif record[4]=="241":
				tpOo= "NCN"
			elif record[4]=="242":
				tpOo= "NCE"	
				
			txOo = record[6] #tax
			
#			if record[8]==1:
#				aeOo="Afecto"
#			elif record[8]==2:
#				#txOo= '0'
#				aeOo="Exento"
			
			unOo = record[5] #untax
			toOo = record[7] #total
			
			sum_ae += aeOo
			sum_tx += txOo
			sum_un += unOo
			sum_to += toOo
			
			if cl==56:
				#OoO={'auxiliar':'tT'}				
				#d.append(OoO)
				print str(self.formatLang(aeS, digits=0)),type(self.formatLang(aeS, digits=0)),self.formatLang(aeS, digits=0)
				OoO={
					'number': '', 
					'x_tipo_doc': '',
					'date_invoice': '',
					'rut': '',
					'cliente': '',
					#'afe_exe': str(self.formatLang(aeS, digits=0)),
					#'cc_amount_tax': str(self.formatLang(txS, digits=0)),
					#'cc_amount_untaxed': str(self.formatLang(unS, digits=0)),
					#'cc_amount_total': str(self.formatLang(toS, digits=0)),
					'afe_exe': aeS,
					'cc_amount_tax': txS,
					'cc_amount_untaxed': unS,
					'cc_amount_total': toS,
					'auxiliar':'dT'
				}	
				d.append(OoO)
				
				aeS=0
				txS=0
				unS=0  
				toS=0 
				cl=0
				
				d.append({'auxiliar':'t',})			
				
			OoO={
				'number': nmOo, 
				'x_tipo_doc': tpOo,
				'date_invoice': dtOo,
				'rut': rtOo,
				'cliente': clOo,
				#'afe_exe':str(self.formatLang(aeOo, digits=0)),
				#'cc_amount_tax': str(self.formatLang(txOo, digits=0)),
				#'cc_amount_untaxed': str(self.formatLang(unOo, digits=0)),
				#'cc_amount_total': str(self.formatLang(toOo, digits=0)),
				'afe_exe':aeOo,
				'cc_amount_tax': txOo,
				'cc_amount_untaxed': unOo,
				'cc_amount_total': toOo,
				'auxiliar':'d'
				}	
			
			aeS+=aeOo	
			txS+=txOo
			unS+=unOo
			toS+=toOo
			
			d.append(OoO)							
			
			cl+=1
			
		#preguntar k onda
		OoO={
			'number': '', 
			'x_tipo_doc': '',
			'date_invoice': '',
			'rut': '',
			'cliente': 'SUB TOTAL',
			# 'afe_exe':str(self.formatLang(aeS, digits=0)),
			# 'cc_amount_tax': str(self.formatLang(txS, digits=0)),
			# 'cc_amount_untaxed': str(self.formatLang(unS, digits=0)),
			# 'cc_amount_total': str(self.formatLang(toS, digits=0)),
			'afe_exe':aeS,
			'cc_amount_tax': txS,
			'cc_amount_untaxed': unS,
			'cc_amount_total': toS,
			'auxiliar':'dT'
			}	
		d.append(OoO)
		
		aeS=0
		txS=0
		unS=0  
		toS=0
		
		OoO={
			'number': '', 
			'x_tipo_doc': '',
			'date_invoice': '',
			'rut': '',
			'cliente': 'TOTAL',
			# 'afe_exe':str(self.formatLang(sum_ae, digits=0)),
			# 'cc_amount_tax': str(self.formatLang(sum_tx, digits=0)),
			# 'cc_amount_untaxed': str(self.formatLang(sum_un, digits=0)),
			# 'cc_amount_total': str(self.formatLang(sum_to, digits=0)),
			'afe_exe':sum_ae,
			'cc_amount_tax': sum_tx,
			'cc_amount_untaxed': sum_un,
			'cc_amount_total': sum_to,
			'auxiliar':'dT'
			}

		d.append(OoO)	
#		d.append(arrInfAgrupado)	
		return d
	
	def nuevo(self,co,pe,si,ty):
		data=[]
		periodos = ",".join(map(str,pe))
		sql="""
		select id, name from account_journal aj where id in (
		select journal_id  
		from account_invoice ai 
		where ai.state not in ('draft', 'cancel') 
		and ai.period_id in ({0}) 
		and ai.company_id = {1} 
		)
		and aj.code between '200' and '299'
		""".format(periodos,str(co[0]))
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,{'id':record[0],
									'name':record[1],
									} )
			
		return data
	def detalle(self,journal_id,co,pe,si,ty):
		data = []
		periodos = ",".join(map(str,pe))
		sql="""
		
		SELECT ai.number
		,date_invoice
		,rp.vat
		, rp.name
		, ai.amount_untaxed
		,	ai.amount_tax
		, ai.amount_total
		,   (
			select 
			CASE WHEN sum(ait.base_amount) is null 
			then 0 else sum(ait.base_amount) 
			end as a 
			from account_invoice_tax ait 
			where UPPER(ait.name) like UPPER('%exento%') 
			and ait.invoice_id = ai.id
		) base_amount
		
		FROM   public.account_invoice ai
		,   public.res_partner rp 
		WHERE ai.state not in ('draft', 'cancel') 
		and  ai.partner_id = rp.id 
		AND  ai.journal_id = {0} 
		and  ai.period_id in ({1}) 
		and 	ai.company_id = {2} 
		order by  ai.number
		
		 """.format(journal_id, periodos, str(co[0]))
		
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,
					{
					
										'number': record[0], 
										'x_tipo_doc': "",
										'date_invoice': record[1],
										'rut': record[2],
										'cliente': record[3],
										# 'afe_exe':str(self.formatLang(record[7], digits=0)),
										# 'cc_amount_tax': str(self.formatLang(record[5], digits=0)),
										# 'cc_amount_untaxed': str(self.formatLang(record[4], digits=0)),
										# 'cc_amount_total': str(self.formatLang(record[6], digits=0)),
										'afe_exe':record[7],
										'cc_amount_tax': record[5],
										'cc_amount_untaxed': record[4],
										'cc_amount_total': record[6],
										'auxiliar':'d'
					
					})
		return data

	def subtotales(self,journal_id,co,pe):
		periodos = ",".join(map(str,pe))
		data=[]
		sql="""SELECT 
				count(*) as cantidad
			  ,	sum(ai.amount_untaxed) amount_untaxed
			  , sum(ai.amount_tax) amount_tax
			  , sum(ai.amount_total) amount_total
			  , sum((
			   select 
			   CASE WHEN sum(ait.base_amount) is 
			    null 
			   then 0 else sum(ait.base_amount) 
			   end as a 
			   from account_invoice_tax ait 
			   where UPPER(ait.name) like UPPER('%exento%') 
			   and ait.invoice_id = ai.id
			  )) base_amount
			  
			  FROM   public.account_invoice ai
			  ,   public.res_partner rp 
			  WHERE ai.state not in ('draft', 'cancel') 
			  and  ai.partner_id = rp.id 
			  AND  ai.journal_id = {0} 
			  and  ai.period_id in ({1}) 
			  and  ai.company_id = {2}	
		""".format(journal_id, periodos, str(co[0]))
		print(sql)
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,
					{
					# 'cantidad':str(self.formatLang(record[0], digits=0))
					# ,'base_amount':str(self.formatLang(record[4], digits=0))
					# ,'amount_untaxed':record[1]
					# ,'amount_tax':str(self.formatLang(record[2], digits=0))
					# ,'amount_total':str(self.formatLang(record[3], digits=0))
					'cantidad':record[0],
					'base_amount':record[4],
					'amount_untaxed':record[1],
					'amount_tax':record[2],
					'amount_total':record[3],
					
					})
		return data

	def totales(self,co,pe):
		periodos = ",".join(map(str,pe))
		data=[]
		sql="""select sum(cantidad) cantidad, sum(amount_untaxed) amount_untaxed, sum(amount_tax) amount_tax,sum(amount_total) amount_total, sum(base_amount) base_amount 

from (
select 	count(*) as cantidad
			  ,	coalesce(sum(ai.amount_untaxed),0) amount_untaxed
			  , coalesce(sum(ai.amount_tax),0) amount_tax
			  , coalesce(sum(ai.amount_total),0) amount_total
			  , coalesce(sum((
			   select 
			   CASE WHEN sum(ait.base_amount) is 
			    null 
			   then 0 else sum(ait.base_amount) 
			   end as a 
			   from account_invoice_tax ait 
			   where UPPER(ait.name) like UPPER('%exento%') 
			   and ait.invoice_id = ai.id
			  )),0) base_amount
			  
			  FROM   public.account_invoice ai	
			  ,   public.res_partner rp 
			  WHERE ai.state not in ('draft', 'cancel') 
			  and  ai.partner_id = rp.id 
			  AND  ai.journal_id in (
				select id from account_journal aj where aj.code between '200' and '299' and not 
				UPPER(name) like UPPER('%nota%') and not UPPER(name) like UPPER('%credito%') and ai.company_id = {1}
			  )
			  and  ai.period_id in ({0}) 
			  and  ai.company_id = {1}
union 

select 	count(*) as cantidad
			  ,	coalesce(sum(ai.amount_untaxed),0)*-1 amount_untaxed
			  , coalesce(sum(ai.amount_tax),0)*-1 amount_tax
			  , coalesce(sum(ai.amount_total),0)*-1 amount_total
			  , coalesce(sum((
			   select 
			   CASE WHEN sum(ait.base_amount) is 
			    null 
			   then 0 else sum(ait.base_amount) 
			   end as a 
			   from account_invoice_tax ait 
			   where UPPER(ait.name) like UPPER('%exento%') 
			   and ait.invoice_id = ai.id
			  )),0)*-1 base_amount
			  
			  FROM   public.account_invoice ai
			  ,   public.res_partner rp 
			  WHERE ai.state not in ('draft', 'cancel') 
			  and  ai.partner_id = rp.id 
			  AND  ai.journal_id in (
				select id from account_journal aj where aj.code between '200' and '299' and 
				UPPER(name) like UPPER('%nota%') and  UPPER(name) like UPPER('%credito%') and ai.company_id = {1}
			  )
			  and  ai.period_id in ({0}) 
			  and  ai.company_id = {1}
			  ) as a
		""".format( periodos, str(co[0]))

		print(sql)
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,
					{
					# 'cantidad':str(self.formatLang(record[0], digits=0))
					# ,'base_amount':str(self.formatLang(record[4], digits=0))
					# ,'amount_untaxed':str(self.formatLang(record[1], digits=0))
					# ,'amount_tax':str(self.formatLang(record[2], digits=0))
					# ,'amount_total':str(self.formatLang(record[3], digits=0))
					'cantidad':record[0],
					'base_amount':record[4],
					'amount_untaxed':record[1],
					'amount_tax':record[2],
					'amount_total':record[3],
					
					})
		return data
