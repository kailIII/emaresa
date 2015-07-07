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
		'time': time,
		'_periodos': self._periodos,
		'corto_dat': self.corto_dat,
		'get_': self.get_,
		})
	def _periodos(self, period_list):
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
	def corto_dat(self,arg1):	
		if len(arg1)>28:
			descripcion=arg1[:27]
		else:
			descripcion=arg1	
		return descripcion				
	def get_(self,co,pe,si,ty):   
		
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
		#cuenta_lineas=0
		#calculo_pasivo=0
		#calculo_activo=0
		#sum_deb_cc=0
		#sum_cre_cc=0				
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
           		'auxiliar':'t'     
           		}	
		data.append(obj_b)							
		for period_id in pe:           
			Lids = Lids + str(period_id) + ","				
		while cc<len(Lids)-1:				
			Lids_= Lids_ + Lids[cc]
			cc=cc + 1
		self.cr.execute("select aa.code,aa.name,aat.code,sum(aml.debit),sum(aml.credit) from account_move_line aml,account_account aa,account_account_type aat where aml.account_id=aa.id and aa.user_type = aat.id and aml.state='valid' and aml.company_id = " + str(co[0]).encode("utf-8") + " and aml.period_id in ("+"".join(map(str, Lids_))+") group by aa.code,aa.name,aat.code order by aa.code")	
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
				if calculo_>0:
					deudor=calculo_
				else:
					if calculo_<0:
						acreedor=calculo_ * -1					
					else:
						acreedor=calculo_
				if tipoCta=='Activos' or tipoCta=='Pasivos' or tipoCta=='Patrimonio':
					if deudor>0:
						activo=deudor
					if acreedor>0:
						pasivo=acreedor
				if tipoCta=='Egresos':
					if deudor>0:
						perdida=deudor
					if acreedor>0:
						ganancia=acreedor					
				if tipoCta=='Ingresos':
					if deudor>0:
						perdida=deudor
					if acreedor>0:
						ganancia=acreedor					

				obj_b={
						'code': codeCta,         
						'name': nameCta,
						'debe': self.formatLang(debitos, digits=0),         
						'haber': self.formatLang(credito, digits=0),    
						'deudor': self.formatLang(deudor, digits=0),    
						'acreedor': self.formatLang(acreedor, digits=0),    
						'activo': self.formatLang(activo, digits=0),    
						'pasivo': self.formatLang(pasivo, digits=0),    
						'perdida': self.formatLang(perdida, digits=0),    
						'ganancia': self.formatLang(ganancia, digits=0),    
						'auxiliar':'d'     
						}					
				data.append(obj_b)	
				suma_debe = suma_debe + float(debitos)
				suma_haber = suma_haber + float(credito)
				suma_deudor = suma_deudor + float(deudor)
				suma_acreedor = suma_acreedor + float(acreedor)
				suma_activo = suma_activo + float(activo)
				suma_pasivo = suma_pasivo + float(pasivo)
				suma_perdida = suma_perdida + float(perdida)
				suma_ganancia = suma_ganancia + float(ganancia)				
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
                       	'auxiliar':'d'     
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
                       	'auxiliar':'d'     
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
						'auxiliar':'t'     
						}
					data.append(obj_b)
					cl=0
#		if cl>0:
#			calDif=56-cl					
#			i = 0
#			while i <= calDif:
#				obj_b={
#					'code': ' ',         
#					'name': ' ',
#					'debe': ' ',
#					'haber': ' ',    
#					'deudor': ' ',
#					'acreedor': ' ',
#            		'activo': ' ',
#					'pasivo': ' ',
#                    'perdida': ' ',
#                    'ganancia': ' ',
#                    'auxiliar':'d'     
#                    }	
#				data.append(obj_b)
#				i = i + 1 												
#				obj_b={
#			'code': '',         
#			'name': '',
#			'debe': 'Debe',         
#			'haber': 'Haber',    
#			'deudor': 'Deudor',    
#			'acreedor': 'Acreedor',    
#			'activo': 'Activo',    
#			'pasivo': 'Pasivo',    
#			'perdida': 'Perdida',    
#			'ganancia': 'Ganancia',    
#			'auxiliar':'d_'     
#			}	
#		data.append(obj_b)

		obj_b={
			'code': '',         
			'name': 'SUB TOTAL',
			'debe': self.formatLang(suma_debe,digits=0),         
			'haber': self.formatLang(suma_haber,digits=0),    
			'deudor': self.formatLang(suma_deudor,digits=0),    
			'acreedor': self.formatLang(suma_acreedor,digits=0),    
			'activo': self.formatLang(suma_activo,digits=0),    
			'pasivo': self.formatLang(suma_pasivo,digits=0),    
			'perdida': self.formatLang(suma_perdida,digits=0),    
			'ganancia': self.formatLang(suma_ganancia,digits=0),    
			'auxiliar':'d_'     
			}
		data.append(obj_b)     
		calculo_pasivo = float(suma_activo) - float(suma_pasivo)
		calculo_activo = float(suma_ganancia) - float(suma_perdida)
		if calculo_pasivo<0:
			calculo_pasivo = calculo_pasivo * -1
		if calculo_activo<0:
			calculo_activo = calculo_activo * -1
#		if calculo_pasivo==0:
#			calculo_pasivo='0'
#		if calculo_activo==0:
#			calculo_activo='0'

		obj_b={
			'code': '',         
			'name': 'RESULTADO DEL EJERCICIO',
			'debe': '0',         
			'haber': '0',    
			'deudor': '0',    
			'acreedor': '0',    
			'activo': '0',    
			'pasivo': '0',    
			'perdida': '0',    
			'ganancia':'0',    
			'auxiliar':'d_'     
			}
		
		if suma_activo != suma_pasivo:
			if suma_activo < suma_pasivo:
				obj_b['activo'] = int(calculo_pasivo)

			elif suma_pasivo < suma_activo:
				obj_b['pasivo'] = int(calculo_pasivo)

		if suma_perdida	!= suma_ganancia:
			if suma_perdida < suma_ganancia:
				obj_b['perdida'] = int(calculo_pasivo)

			if suma_ganancia < suma_perdida:
				obj_b['ganancia'] = int(calculo_pasivo)


		data.append(obj_b)  
		
		#la diferencia del activo vs el pasivo y la perdida vs la ganancia debe asignarse al monto menor  
		#pas_aux=float(suma_pasivo)+float(calculo_pasivo)
		#per_aux=float(suma_perdida)+float(calculo_activo)
		#if pas_aux<0:
		#	pas_aux = pas_aux * -1
		#if per_aux<0:
		#	per_aux = per_aux * -1	
		
		if suma_activo != suma_pasivo:
			if suma_activo < suma_pasivo:
				suma_activo += calculo_pasivo
			elif suma_pasivo < suma_activo:
				suma_pasivo += calculo_pasivo
		
		if suma_perdida	!= suma_ganancia:
			if suma_perdida < suma_ganancia:
				suma_perdida += calculo_activo
			elif suma_ganancia < suma_perdida:
				suma_ganancia += calculo_activo
			
		obj_b={
			'code': '',         
			'name': 'TOTAL',
			'debe': self.formatLang(suma_debe,digits=0),         
			'haber': self.formatLang(suma_haber,digits=0),    
			'deudor': self.formatLang(suma_deudor,digits=0),    
			'acreedor': self.formatLang(suma_acreedor,digits=0),    
			'activo': self.formatLang(suma_activo,digits=0),    
			'pasivo': self.formatLang(suma_pasivo,digits=0),    
			'perdida': self.formatLang(suma_perdida,digits=0),    
			'ganancia': self.formatLang(suma_ganancia,digits=0),    
			'auxiliar':'d_'     
			}
		data.append(obj_b)		
		return data       
