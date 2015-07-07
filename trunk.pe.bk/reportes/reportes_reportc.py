import time
from report import report_sxw

import logging
_logger = logging.getLogger('reportes')


class reportes_reportc( report_sxw.rml_parse ):
	
	
	def __init__(self,cr,uid,name,context):
		super(reportes_reportc,self).__init__(cr,uid,name,context=context)
		self.localcontext.update({
		'time': time,
		'_periodos_v': self._periodos_v,
		'corto_dat_v': self.corto_dat_v,
		'get__v': self._get__v,
		'nuevo':self.nuevo
		,'detalle':self.detalle
		,'subtotales':self.subtotales
		,'totales':self.totales
		
		})
		
		
		
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
		Lds=''
		Lds_=''
		cc=0	
		#cl=0	
		tpOo= 0
		aeOo= 0
		aeS=0
		txS=0
		unS=0  
		toS=0 
		cl=0 
		aeT=0
		txT=0
		unT=0
		toT=0
		
		
		d.append({'auxiliar':'t',})							
		
		for p in pe:           
			Lds = Lds + str(p) + ","				
			
		while cc<len(Lds)-1:				
			Lds_= Lds_ + Lds[cc]
			cc=cc + 1
		
		#print("construyo la query")
		sql = "SELECT ai.reference,date_invoice,rp.vat, rp.name, aj.code, ai.amount_untaxed,	ai.amount_tax, ai.amount_total,   ai.fiscal_position, (select CASE WHEN sum(ait.base_amount) is null then 0 else sum(ait.base_amount) end as a from account_invoice_tax ait where UPPER(ait.name) like UPPER('%exento%') and ait.invoice_id = ai.id) base_amount 	FROM   public.account_invoice ai,   public.account_journal aj,   public.res_partner rp WHERE ai.state not in ('draft', 'cancel') and  ai.partner_id = rp.id AND  aj.id = ai.journal_id and aj.code between '100' and '142' and  ai.period_id in ("+"".join(map(str, Lds_))+") and 	ai.company_id = "+ str(co[0]) + "  order by aj.cod"
		print(sql)
		
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			#print("recorro la query")
			nmOo = record[0]
			dtOo = record[1]
			rtOo = record[2]
			clOo = record[3]		
			tpOo = ""
			aeOo = record[9]
						
			if record[4]=="101":
				tpOo= "FN"
			elif record[4]=="102":
				tpOo= "FE"
			elif record[4]=="103":
				tpOo= "FI"	
			elif record[4]=="":
				tpOo= "SC"	
				
			txOo = record[6] #tax
			
			#if record[8]==1:
				#aeOo="Afecto"
			#elif record[8]==2:
				#txOo= '0'
				#aeOo="Exento"
			
			unOo = record[5] #untaxed
			toOo = record[7] #total
			
			if cl==56:
				#OoO={'auxiliar':'tT'}				
				#d.append(OoO)
				OoO={
					'number': '', 
					'x_tipo_doc': '',
					'date_invoice': '',
					'vat': '',
					'proveedor': 'SUB TOTAL',
					'afe_exe':self.formatLang(aeS, digits=0),
					'iva': self.formatLang(txS, digits=0),
					'neto_': self.formatLang(unS, digits=0),
					'total_': self.formatLang(toS, digits=0),
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
				'vat': rtOo,
				'proveedor': clOo,
				'afe_exe':self.formatLang(aeOo, digits=0),
				'iva': self.formatLang(txOo, digits=0),
				'neto_': self.formatLang(unOo, digits=0),
				'total_': self.formatLang(toOo, digits=0),
				'auxiliar':'d'
				}	
			#sub total
			aeS+=aeOo	
			txS+=txOo
			unS+=unOo
			toS+=toOo
			
			d.append(OoO)							
			#total final
			aeT+=aeOo
			txT+=txOo
			unT+=unOo
			toT+=toOo
			
			cl=cl+1
			
		#preguntar k onda
		OoO={
					'number': '', 
					'x_tipo_doc': '',
					'date_invoice': '',
					'vat': '',
					'proveedor': 'SUB TOTAL',
					'afe_exe':self.formatLang(aeS, digits=0),
					'iva': self.formatLang(txS, digits=0),
					'neto_': self.formatLang(unS, digits=0),
					'total_': self.formatLang(toS, digits=0),
					'auxiliar':'dT'
				}	
		d.append(OoO)
		OoO={
			'number': '', 
			'x_tipo_doc': '',
			'date_invoice': '',
			'vat': '',
			'proveedor': 'TOTAL',
			'afe_exe':self.formatLang(aeT, digits=0),
			'iva': self.formatLang(txT, digits=0),
			'neto_': self.formatLang(unT, digits=0),
			'total_': self.formatLang(toT, digits=0),
			'auxiliar':'dT'
			}	
		d.append(OoO)
		aeS=0
		txS=0
		unS=0  
		toS=0
			
			
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
		and aj.code between '100' and '142'
		order by aj.code 
		""".format(periodos,str(co[0]))
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,{'id':record[0],
									'name':record[1],
									} )
			
		return data
	'''def detalle(self,journal_id,co,pe,si,ty):
		data = []
		periodos = ",".join(map(str,pe))
		sql="""select
		ai.reference
		,date_invoice
		,rp.vat
		, rp.name
		, ai.amount_untaxed
		, ai.amount_tax
		, ai.amount_total
		,   ai.fiscal_position
		, (select CASE WHEN sum(ait.base_amount) is null then 0 
		else sum(ait.base_amount) end as a 
		from account_invoice_tax ait 
		where UPPER(ait.name) like UPPER('%iva%') 
		and ait.invoice_id = ai.id) base_amount 	

		FROM   public.account_invoice ai
		,   public.res_partner rp 
		
		WHERE ai.state not in ('draft', 'cancel') 
		and  ai.partner_id = rp.id 
		AND  ai.journal_id = {0} 
		and  ai.period_id in ({1}) 
		and 	ai.company_id = {2} 
		order by date_invoice;
		
		 """.format(journal_id, periodos, str(co[0]))
		
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,
					{
						'number': record[0], 
						'x_tipo_doc': "",
						'date_invoice': record[1],
						'vat': record[2],
						'proveedor': record[3],
						'afe_exe':self.formatLang(record[8], digits=0),
						'cc_amount_untaxed': self.formatLang(record[5], digits=0),
						'cc_amount_tax': self.formatLang(record[4], digits=0),
						'cc_amount_total': self.formatLang(record[6], digits=0),
						'auxiliar':'d'
				})
			
			#							'number': record[0], 
			#							'x_tipo_doc': "",
			#							'date_invoice': record[1],
			#							'vat': record[2],
			#							'cliente': record[3],
			#							'afe_exe':self.formatLang(record[7], digits=0),
			#							'cc_amount_tax': self.formatLang(record[5], digits=0),
			#							'cc_amount_untaxed': self.formatLang(record[4], digits=0),
			#							'cc_amount_total': self.formatLang(record[6], digits=0),
			#							'auxiliar':'d'
					
					
		return data'''

    #la palabra exento cambia la columna de exento#
	def detalle(self,journal_id,co,pe,si,ty):
		data = []
		periodos = ",".join(map(str,pe))
		sql="""select
		ai.reference
		,date_invoice
		,rp.vat
		, rp.name
		, ai.amount_untaxed
		, ai.amount_tax
		, ai.amount_total
		,   ai.fiscal_position
		, (select CASE WHEN sum(ait.base_amount) is null then 0 
		else sum(ait.base_amount) end as a 
		from account_invoice_tax ait 
		where UPPER(ait.name) like UPPER('%exento%') 
		and ait.invoice_id = ai.id) base_amount 	

		FROM   public.account_invoice ai
		,   public.res_partner rp 
		
		WHERE ai.state not in ('draft', 'cancel') 
		and  ai.partner_id = rp.id 
		AND  ai.journal_id = {0} 
		and  ai.period_id in ({1}) 
		and 	ai.company_id = {2} 
		order by date_invoice;
		
		 """.format(journal_id, periodos, str(co[0]))
		
		self.cr.execute(sql)
		for record in self.cr.fetchall():
			data.insert(len(data)+1,
					{
						'number': record[0], 
						'x_tipo_doc': "",
						'date_invoice': record[1],
						'vat': record[2],
						'proveedor': record[3],
						'afe_exe':self.formatLang(record[8], digits=0),
						'cc_amount_untaxed': self.formatLang(record[5], digits=0),
						'cc_amount_tax': self.formatLang(record[4]-record[8], digits=0),
						'cc_amount_total': self.formatLang(record[6], digits=0),
						'auxiliar':'d'
				})
			
			#							'number': record[0], 
			#							'x_tipo_doc': "",
			#							'date_invoice': record[1],
			#							'rut': record[2],
			#							'cliente': record[3],
			#							'afe_exe':self.formatLang(record[7], digits=0),
			#							'cc_amount_tax': self.formatLang(record[5], digits=0),
			#							'cc_amount_untaxed': self.formatLang(record[4], digits=0),
			#							'cc_amount_total': self.formatLang(record[6], digits=0),
			#							'auxiliar':'d'
					
					
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
					'cantidad':self.formatLang(record[0], digits=0)
					,'base_amount':self.formatLang(record[4], digits=0)
					,'amount_untaxed':self.formatLang(record[1]-record[4], digits=0)
					,'amount_tax':self.formatLang(record[2], digits=0)
					,'amount_total':self.formatLang(record[3], digits=0)
					
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
				select id from account_journal aj where aj.code between '100' and '199' and not 
				UPPER(name) like UPPER('%nota%') and not UPPER(name) like UPPER('%credito%') and  ai.company_id = {1}
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
			   where UPPER(ait.name) like UPPER('%iva%') 
			   and ait.invoice_id = ai.id
			  )),0)*-1 base_amount
			  
			  FROM   public.account_invoice ai
			  ,   public.res_partner rp 
			  WHERE ai.state not in ('draft', 'cancel') 
			  and  ai.partner_id = rp.id 
			  AND  ai.journal_id in (
				select id from account_journal aj where aj.code between '100' and '199' and 
				UPPER(name) like UPPER('%nota%') and  UPPER(name) like UPPER('%credito%') and  ai.company_id = {1}
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
					'cantidad':self.formatLang(record[0], digits=0)
					,'base_amount':self.formatLang(record[4], digits=0)
					,'amount_untaxed':self.formatLang(record[1]-record[4], digits=0)
					,'amount_tax':self.formatLang(record[2], digits=0)
					,'amount_total':self.formatLang(record[3], digits=0)
					
					})
		return data


report_sxw.report_sxw('report.reportes_print_libcom', 'reportes',
      'addons/reportes/reportes_reportc.rml', parser=reportes_reportc, header=False)
