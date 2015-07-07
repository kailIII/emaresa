import time
from report import report_sxw
class reportes_reportv( report_sxw.rml_parse ):
	def __init__(self,cr,uid,name,context):
		super(reportes_reportv,self).__init__(cr,uid,name,context=context)
		self.localcontext.update({
		'time': time,
		'_periodosv': self._periodosv,
		'corto_datv': self.corto_datv,
		'get_v': self._get_v,
		})
		
	def _periodosv(self, period_list):
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
		
	def corto_datv(self,arg1):	
		largo=len(arg1)	
		if largo>28:
			descripcion=arg1[0]+arg1[1]+arg1[2]+arg1[3]+arg1[4]+arg1[5]+arg1[6]+arg1[7]+arg1[8]+arg1[9]+arg1[10]+arg1[11]+arg1[12]+arg1[13]+arg1[14]+arg1[15]+arg1[16]+arg1[17]+arg1[18]+arg1[19]+arg1[20]+arg1[21]+arg1[22]+arg1[23]+arg1[24]+arg1[25]+arg1[26]+arg1[27]
		else:
			descripcion=arg1	
		return descripcion				
		
	def _get_v(self,co,pe,si,ty):        
		data = []		
		Lids=''
		Lids_=''
		cc=0			
		cl=0
		suma_debe = 0
		suma_haber = 0
		suma_deudor = 0
		suma_acreedor = 0
		suma_activo = 0
		suma_pasivo = 0
		suma_perdida = 0
		suma_ganancia = 0                                 
		cuenta_lineas=0
		calculo_pasivo=0
		calculo_activo=0
		sum_deb_cc=0
		sum_cre_cc=0				
		obj_b={
           		'code': 'Codigo',         
           		'name': 'Cuenta',
           		'debe': 'Debe',         
           		'haber': 'Haber',    
           		'deudor': 'Deudor',    
           		'acreedor': 'Acreedor',    
           		'activo': 'Activo',    
           		'pasivo': 'Pasivo',    
           		'perdida': 'Perdida',    
           		'ganancia': 'Ganancia',    
           		'msilva':'titulos8'     
           		}	
		data.append(obj_b)							
		for period_id in pe:           
			Lids = Lids + str(period_id) + ","				
		while cc<len(Lids)-1:				
			Lids_= Lids_ + Lids[cc]
			cc=cc + 1
		sql = "select aa.code,aa.name,aat.name,sum(aml.debit),sum(aml.credit) from account_move_line aml,account_account aa,account_account_type aat where aml.account_id=aa.id and aa.user_type = aat.id and aml.state='valid' and aml.company_id = " + str(co[0]).encode("utf-8") + " and aml.period_id in ("+"".join(map(str, Lids_))+") group by aa.code,aa.name,aat.name order by aa.code"
		self.cr.execute(sql)	
		print sql
		for record in self.cr.fetchall():
			codeCta= record[0]
			nameCta= record[1]
			tipoCta= record[2]
			debitos= record[3]
			credito= record[4]			
			if debitos > 0 or credito > 0:
				calculo_= float(debitos) - float(credito)
				deudor=0
				acreedor=0
				activo=0
				pasivo=0
				perdida=0
				ganancia=0					
				if float(debitos) > float(credito):
					deudor=calculo_					
					if tipoCta=='Activos':
						activo = calculo_
					if tipoCta=='Pasivos':
						activo = calculo_
					if tipoCta=='Ingresos':
						perdida=calculo_						
				else:
					acreedor=calculo_
					if tipoCta=='Activos':
						pasivo = calculo_
					if tipoCta=='Pasivos':
						pasivo = calculo_
					if tipoCta=='Egresos':
						ganancia = calculo_		
				if debitos==0:
					debitos='0'
				if credito==0:
					credito='0'
				if deudor==0:
					deudor='0'
				if acreedor==0:
					acreedor='0'
				if activo==0:
					activo='0'
				if pasivo==0:
					pasivo='0'
				if perdida==0:
					perdida='0'
				if ganancia==0:
					ganancia='0'                
				if debitos<0:
					aux_val=str(debitos)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					debitos_sn = aux_sinbolo
				else:
					debitos_sn = debitos
				if credito<0:
					aux_val=str(credito)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					credito_sn = aux_sinbolo
				else:
					credito_sn = credito
				if deudor<0:
					aux_val=str(deudor)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					deudor_sn = aux_sinbolo
				else:
					deudor_sn = deudor
				if acreedor<0:
					aux_val=str(acreedor)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					acreedor_sn = aux_sinbolo
				else:
					acreedor_sn = acreedor					
				if activo<0:
					aux_val=str(activo)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					activo_sn = aux_sinbolo
				else:
					activo_sn = activo	
				if perdida<0:
					aux_val=str(perdida)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					perdida_sn = aux_sinbolo
				else:
					perdida_sn = perdida						
				if pasivo<0:
					aux_val=str(pasivo)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					pasivo_sn = aux_sinbolo
				else:
					pasivo_sn = pasivo	
				if ganancia<0:
					aux_val=str(ganancia)
					aux_largo=len(aux_val)-1                     
					aux_sinbolo=""
					i = 1
					while i <= aux_largo:
						aux_sinbolo=aux_sinbolo+aux_val[i]
						i = i + 1                                                                                    	
					ganancia_sn = aux_sinbolo
				else:
					ganancia_sn = ganancia						
				obj_b={
						'code': codeCta,         
						'name': nameCta,
						'debe': debitos_sn,         
						'haber': credito_sn,    
						'deudor': deudor_sn,    
						'acreedor': acreedor_sn,    
						'activo': activo_sn,    
						'pasivo': pasivo_sn,    
						'perdida': perdida_sn,    
						'ganancia': ganancia_sn,    
						'msilva':'data8'     
						}					
				data.append(obj_b)	
				suma_debe = suma_debe + float(debitos)
				suma_haber = suma_haber + float(credito)
				suma_deudor = suma_deudor + float(deudor)
				suma_acreedor = suma_acreedor + float(acreedor)
				suma_activo = suma_activo + float(activo)
				suma_pasivo = suma_pasivo + float(pasivo)
				suma_perdida = suma_perdida + float(ganancia)
				suma_ganancia = suma_ganancia + float(perdida)				
				cl=cl+1 
				if cl==55:
					obj_b={
						'code': ' ',         
						'name': ' ',
						'debe': ' ',
						'haber': ' ',    
						'deudor': ' ',
						'acreedor': ' ',
                       	'activo': ' ',
                       	'pasivo': ' ',
                       	'perdida': ' ',
                       	'ganancia': ' ',
                       	'msilva':'data8'     
                       	}
					data.append(obj_b)
					obj_b={
						'code': ' ',         
						'name': ' ',
						'debe': ' ',
						'haber': ' ',    
						'deudor': ' ',
						'acreedor': ' ',
                       	'activo': ' ',
                       	'pasivo': ' ',
                       	'perdida': ' ',
                       	'ganancia': ' ',
                       	'msilva':'data8'     
                       	}
					data.append(obj_b)
					obj_b={
						'code': 'Codigo',      		   
						'name': 'Cuenta',
						'debe': 'Debe',         
						'haber': 'Haber',    
						'deudor': 'Deudor',    
						'acreedor': 'Acreedor',    
						'activo': 'Activo',    
						'pasivo': 'Pasivo',    
						'perdida': 'Perdida',    
						'ganancia': 'Ganancia',    
						'msilva':'titulos8'     
						}
					data.append(obj_b)
					cl=0
		if cl>0:
			calDif=56-cl					
			i = 0
			while i <= calDif:
				obj_b={
					'code': ' ',         
					'name': ' ',
					'debe': ' ',
					'haber': ' ',    
					'deudor': ' ',
					'acreedor': ' ',
            		'activo': ' ',
					'pasivo': ' ',
                    'perdida': ' ',
                    'ganancia': ' ',
                    'msilva':'data8'     
                    }	
				data.append(obj_b)
				i = i + 1 												
		obj_b={
			'code': '',         
			'name': '',
			'debe': 'Debe',         
			'haber': 'Haber',    
			'deudor': 'Deudor',    
			'acreedor': 'Acreedor',    
			'activo': 'Activo',    
			'pasivo': 'Pasivo',    
			'perdida': 'Perdida',    
			'ganancia': 'Ganancia',    
			'msilva':'data8_'     
			}	
		data.append(obj_b)
		if suma_debe==0:
			suma_debe='0' 
		if suma_haber==0:
			suma_haber='0' 
		if suma_deudor==0:
			suma_deudor='0' 
		if suma_acreedor==0:    
			suma_acreedor='0' 
		if suma_activo==0:
			suma_activo='0' 
		if suma_pasivo==0:
			suma_pasivo='0' 
		if suma_perdida==0:
			suma_perdida='0' 
		if suma_ganancia==0:    
			suma_ganancia='0' 
		if suma_debe<0:
			aux_val=str(suma_debe)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                                                                    	
			suma_debe_sn=aux_sinbolo
		else:
			suma_debe_sn=suma_debe
		if suma_haber<0:
			aux_val=str(suma_haber)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1
			suma_haber_sn=aux_sinbolo
		else:
			suma_haber_sn=suma_haber
		if suma_deudor<0:
			aux_val=str(suma_deudor)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1
			suma_deudor_sn=aux_sinbolo
		else:
			suma_deudor_sn=suma_deudor
		if suma_acreedor<0:
			aux_val=str(suma_acreedor)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1
			suma_acreedor_sn=aux_sinbolo 										                                                                                                  
		else:
			suma_acreedor_sn=suma_acreedor 										                                                                                                  
		if suma_activo<0:
			aux_val=str(suma_activo)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1
			suma_activo_sn=aux_sinbolo
		else:
			suma_activo_sn=suma_activo
		if suma_pasivo<0:
			aux_val=str(suma_pasivo)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1
			suma_pasivo_sn=aux_sinbolo
		else:
			suma_pasivo_sn=suma_pasivo
		if suma_perdida<0:
			aux_val=str(suma_perdida)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                 
			suma_perdida_sn=aux_sinbolo
		else:
			suma_perdida_sn=suma_perdida
		if suma_ganancia<0:
			aux_val=str(suma_ganancia)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                
			suma_ganancia_sn=aux_sinbolo
		else:
			suma_ganancia_sn=suma_ganancia
		obj_b={
			'code': '',         
			'name': 'SUB TOTAL',
			'debe': suma_debe_sn,         
			'haber': suma_haber_sn,    
			'deudor': suma_deudor_sn,    
			'acreedor': suma_acreedor_sn,    
			'activo': suma_activo_sn,    
			'pasivo': suma_pasivo_sn,    
			'perdida': suma_perdida_sn,    
			'ganancia': suma_ganancia_sn,    
			'msilva':'data8_'     
			}
		data.append(obj_b)     
		calculo_pasivo = float(suma_activo) - float(suma_pasivo)
		calculo_activo = float(suma_ganancia) - float(suma_perdida)
		if calculo_pasivo==0:
			calculo_pasivo='0'
		if calculo_activo==0:
			calculo_activo='0'      
		if calculo_pasivo<0:		
			aux_val=str(calculo_pasivo)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                
			calculo_pasivo_sn=aux_sinbolo      
		else:
			calculo_pasivo_sn=calculo_pasivo
		if calculo_activo<0:
			aux_val=str(calculo_activo)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                
			calculo_activo_sn=aux_sinbolo      
		else:
			calculo_activo_sn=calculo_activo
		obj_b={
			'code': '',         
			'name': 'RESULTADO DEL EJERCICIO',
			'debe': '0',         
			'haber': '0',    
			'deudor': '0',    
			'acreedor': '0',    
			'activo': '0',    
			'pasivo': calculo_pasivo_sn,    
			'perdida': calculo_activo_sn,    
			'ganancia':'0',    
			'msilva':'data8_'     
			}
		data.append(obj_b)    
		pas_aux=float(suma_pasivo)+float(calculo_pasivo)
		per_aux=float(suma_perdida)+float(calculo_activo)
		if pas_aux==0:
			pas_aux='0'
		if per_aux==0:
			per_aux='0'		
		if per_aux<0:			
			aux_val=str(per_aux)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                                                
			per_aux_sn=aux_sinbolo         
		else:
			per_aux_sn=per_aux
		if pas_aux<0:
			aux_val=str(pas_aux)
			aux_largo=len(aux_val)-1                     
			aux_sinbolo=""
			i = 1
			while i <= aux_largo:
				aux_sinbolo=aux_sinbolo+aux_val[i]
				i = i + 1                                                                
			pas_aux_sn=aux_sinbolo
		else:
			pas_aux_sn=pas_aux
		obj_b={
			'code': '',         
			'name': 'TOTAL',
			'debe': suma_debe_sn,         
			'haber': suma_haber_sn,    
			'deudor': suma_deudor_sn,    
			'acreedor': suma_acreedor_sn,    
			'activo': suma_activo_sn,    
			'pasivo': pas_aux_sn,    
			'perdida': per_aux_sn,    
			'ganancia': suma_ganancia_sn,    
			'msilva':'data8_'     
			}
		data.append(obj_b)		
		
		return data

report_sxw.report_sxw('report.reportes_print_libven', 
					'reportes',
      				'addons/reportes/reportes_reportv.rml', parser=reportes_reportv, header=True)