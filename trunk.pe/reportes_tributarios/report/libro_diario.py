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
            '_get_period': self._get_period,
            'cortar': self.cortar,
            '_get_move': self._get_move,
        })

    def _get_period(self, period_id):
	if isinstance(period_id, (int,long)):
	        return self.pool.get('account.period').browse(self.cr, self.uid, period_id).name
	elif isinstance(period_id, (list)):
		return self.pool.get('account.period').browse(self.cr, self.uid, period_id[0]).name

    def cortar(self,arg1,largo):	
        if len(arg1)>largo:
            descripcion=arg1[:largo-1]
        else:
            descripcion=arg1	
        return descripcion	
    
    def _get_move(self, period_list, company_id):

        print("--- Entra a Función")

        #auxiliares_=''
        debe_=''
        haber_=''
        suma_debe=0
        suma_haber=0                        
    
        if period_list:
            print("--- Pass Period List")
            pass
        else :
            print("--- Ejecuta ELSE de period list")
            today = time.strftime('%Y-%m-%d')
            self.cr.execute ("select id from account_fiscalyear where date_stop > '%s' and date_start < '%s'"%(today,today))
            fy = self.cr.fetchall()
            self.cr.execute ("select id from account_period where fiscalyear_id = %d"%(fy[0][0]))
            periods = self.cr.fetchall()
            for p in periods :
                period_list[0][2].append(p[0])

            print("--- Termina ELSE de period list")
    
        #if base_on == 'lib_diario':
        #declaracion variables y otros.

        invoice_report=[]        
        cta_lineas=0

        tai_aml = self.pool.get('account.move.line')
        #tai_aa = self.pool.get('account.account')
        #titulos
        obj_b={
                'fecha': 'Fecha',         
                'comprobante': 'Comprobante',
                'vat': 'Vat',
                'partner': 'Cliente/Proveedor',
                'cuenta': 'Cuenta',
                'glosa': 'Glosa',
                'documento': 'Documento',        
                'debe': 'Debe',    
                'haber': 'Haber',        
                'campo':'titulos'     
            }         

        invoice_report.append(obj_b)
        #fin titulos
        for period_id in period_list:
            print("--- Inicia for Period List")
            criteria = [('company_id','=',company_id[0]),
                        ('state','=','valid'),   
                        ('period_id','=',period_id)]
            tai_ids_aml = tai_aml.search(self.cr, self.uid, criteria)       

            for each_cuentas in tai_aml.browse(self.cr, self.uid, tai_ids_aml):
                print("--- Inicia for Period List 2")
                if cta_lineas ==0:
                    auxiliar_id_ = each_cuentas.move_id                           
                if auxiliar_id_ == each_cuentas.move_id:
                    if each_cuentas.move_id.name==False:
                        aux_egreso=' '
                    else:
                        aux_egreso=str(each_cuentas.move_id.name)
                    
#                    comprobante = self.pool.get("account.move").browse(self.cr, self.uid, each_cuentas.move_id.id).name
                    
                    #criterio = [('id','=',each_cuentas.move_id),('company_id','=',company_id[0])]
                    #comprobante = tai_am.search(self.cr,self.uid,criterio)
                     
    
    #                if each_cuentas.move_id.x_tipo==False:
    #                    aux_tipo=' '
    #                else:
    #                    auxiliares = str(each_cuentas.move_id.x_tipo)
    #                    aux_tipo = auxiliares[0] + auxiliares[1] + auxiliares[2]
                        
    #                auxiliares_= str(aux_tipo) + " " + str(aux_egreso)
                    #auxiliares_= str(aux_tipo) + " " + str(aux_egreso)                                                
                    _auxiliares=""
                    if each_cuentas.debit>0:
                        debe_=each_cuentas.debit
                        suma_debe=suma_debe+debe_
                    else:
                        debe_=0
                    if each_cuentas.credit>0:
                        haber_=each_cuentas.credit
                        suma_haber=suma_haber+haber_
                    else:
                        haber_=0
    
                    cta_lineas = cta_lineas + 1
                    obj_b={
                        'fecha': each_cuentas.date,         
                        'comprobante': aux_egreso,
			'vat': each_cuentas.partner_id.vat,
			'partner': each_cuentas.partner_id.name,
                        'cuenta': each_cuentas.account_id.name,
                        'glosa': each_cuentas.ref,
                        'documento': each_cuentas.name, 
                        'debe': self.formatLang(debe_,digits = 0),    
                        'haber': self.formatLang(haber_,digits = 0),        
                        'campo':'data'                                                    
                        }                                                  
                    invoice_report.append(obj_b)               
                else:
                    obj_b={
                        'fecha': 'Totales',         
                        'comprobante': 'Totales',
                        'cuenta': 'Totales',
                        'glosa': 'Totales',
                        'documento': 'Totales', 
                        'debe': self.formatLang(suma_debe,digits = 0),    
                        'haber': self.formatLang(suma_haber,digits = 0),        
                        'campo':'titulos3'                                                    
                    }                                                  
                    invoice_report.append(obj_b)               
    
                    suma_debe=0
                    suma_haber=0
    
                    if each_cuentas.move_id.name==False:
                        aux_egreso=' '
                    else:
                        aux_egreso=str(each_cuentas.move_id.name)
    
    #                if each_cuentas.move_id.x_tipo==False:
    #                    aux_tipo=' '
    #                else:
    #                    #aux_tipo=str(each_cuentas.move_id.x_tipo)
    #                    auxiliares = str(each_cuentas.move_id.x_tipo)
    #                    aux_tipo = auxiliares[0] + auxiliares[1] + auxiliares[2]
                        
    #                auxiliares_= str(aux_tipo) + " " + str(aux_egreso)                        
    
                    if each_cuentas.debit>0:
                        debe_=each_cuentas.debit
                        suma_debe=suma_debe+debe_
                    else:
                        debe_=0
                    if each_cuentas.credit>0:
                        haber_=each_cuentas.credit
                        suma_haber=suma_haber+haber_
                    else:
                        haber_=0
        
                    auxiliar_id_ = each_cuentas.move_id       
                    cta_lineas = cta_lineas + 1
                    obj_b={
                            'fecha': each_cuentas.date,         
                            'comprobante': aux_egreso,
                            'cuenta': each_cuentas.account_id.name,
                            'glosa': each_cuentas.ref,
                            'documento': each_cuentas.name, 
                            'debe': self.formatLang(debe_,digits = 0),    
                            'haber': self.formatLang(haber_,digits = 0),        
                            'campo':'data'                                                    
                        }                                                  
                    invoice_report.append(obj_b)                
                        
                #no sacar esta line :ref muy IMportanTE
            #retorna sabana para el rml each_cuentas.move_id.x_glosa
            print("--- TERMINA FOR")
        print("--- TERMINA FUNCION")
        return invoice_report

report_sxw.report_sxw('report.libro_diario_rml', 'reportes.tributarios', 
            'reportes_tributarios/report/libro_diario.rml', parser=Parser, header=False)
