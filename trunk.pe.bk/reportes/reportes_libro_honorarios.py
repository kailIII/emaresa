import time
from report import report_sxw

import logging
_logger = logging.getLogger('reportes')


class reportes_libro_honorarios( report_sxw.rml_parse ):
	def __init__(self,cr,uid,name,context):
		super(reportes_libro_honorarios,self).__init__(cr,uid,name,context=context)
		self.localcontext.update({
		'time': time,
		'_periodos_v': self._periodos_v,
		'corto_dat_v': self.corto_dat_v,
		'get__v': self._get__v,
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
		
		cl=0 
		sum_total = 0
		sum_tax = 0
		sum_untaxed = 0
		sum_total_subT = 0
		sum_tax_subT = 0
		sum_untaxed_subT = 0
		
		d.append({'auxiliar':'t',})							
		
		for p in pe:           
			Lds = Lds + str(p) + ","				
			
		while cc<len(Lds)-1:				
			Lds_= Lds_ + Lds[cc]
			cc=cc + 1
		

		sql = "SELECT  'BH', ai.number, ai.date_invoice, rp.name, rp.rut, ai.amount_total, ai.amount_tax,ai.amount_untaxed FROM   public.account_invoice ai, res_partner rp WHERE ai.partner_id=rp.id and ai.type='out_invoice' and ai.journal_id=15 and ai.period_id in ("+"".join(map(str, Lds_))+") and ai.company_id = "+ str(co[0])+ " and ai.type='out_invoice' order by ai.date_invoice"
		print(sql)
		self.cr.execute(sql)
		for record in self.cr.fetchall():

			bh = record[0]
			number = record[1]
			Fecha = record[2]
			name = record[3]		
			rut =  record[4]
			am_total = record[5]
			am_tax = record[6]
			am_untaxed = record[7]
			
			#sumatorias para los totales
			sum_total += am_total
			sum_tax += am_tax
			sum_untaxed += am_untaxed
			
			#sumatorias para los subtotales
			sum_total_subT += am_total
			sum_tax_subT += am_tax
			sum_untaxed_subT += am_untaxed
			#contruyo la linea del reporte
			OoO={
					'bh': bh, 
					'number': number,
					'Fecha': self._strip_name(Fecha,30),
					'name': self._strip_name(name, 30),
					'rut': rut,
					'am_total':self.formatLang(sum_total_subT, digits=0),
					'am_tax': self.formatLang(am_untaxed, digits=0),
					'am_untaxed': self.formatLang(am_untaxed, digits=0),
					'auxiliar':'d'
				}
			d.append(OoO)
			
			if cl==56:
				#subtotal por hoja
				OoO={
					'bh': '', 
					'number': '',
					'Fecha': '',
					'name': 'SUB TOTAL',
					'rut': '',
					'am_total':self.formatLang(sum_total_subT, digits=0),
					'am_tax': self.formatLang(sum_tax_subT, digits=0),
					'am_untaxed': self.formatLang(sum_untaxed_subT, digits=0),
					'auxiliar':'dT'
				}	
				d.append(OoO)
				
				sum_total_subT=0
				sum_tax_subT=0
				sum_untaxed_subT=0  
				cl=0
				
				d.append({'auxiliar':'t',})			
				
			cl+=1
			
		#ultimo subtotal
		OoO={
					'bh': '', 
					'number': '',
					'Fecha': '',
					'name': 'SUB TOTAL',
					'rut': '',
					'am_total':self.formatLang(sum_total_subT, digits=0),
					'am_tax': self.formatLang(sum_tax_subT, digits=0),
					'am_untaxed': self.formatLang(sum_untaxed_subT, digits=0),
					'auxiliar':'dT'
				}	
		d.append(OoO)
		
		#Total final
		OoO={
					'bh': '', 
					'number': '',
					'Fecha': '',
					'name': 'TOTAL',
					'rut': '',
					'am_total':self.formatLang(sum_total, digits=0),
					'am_tax': self.formatLang(sum_tax, digits=0),
					'am_untaxed': self.formatLang(sum_untaxed, digits=0),
					'auxiliar':'dT'
				}
			
		d.append(OoO)
		
		return d
	
report_sxw.report_sxw('report.reportes_libro_honorarios', 'reportes',
      'addons/reportes/reportes_libro_honorarios.rml', parser=reportes_libro_honorarios, header=False)
