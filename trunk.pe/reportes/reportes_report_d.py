# 000000000000000000000000000000000000000000000000000000000000000000000000000000
# 1                                                                            1
# 1     LOCALIZACION CHILE OPEN ERP 6.0.3                                      1
# 1     =================================                                      1
# 1     CONSULTOR DE PROCESOS : Paulo Ortiz. (portiz@solintegra.cl)            1
# 1     PROGRAMADOR PYTHON    : Michael Silva (msilva@solintegra.cl)           1
# 1     EMPRESA               : Solintegra Ltda.                               1
# 1     VERSION               : 2.0                                            1
# 1                                                                            1
# 000000000000000000000000000000000000000000000000000000000000000000000000000000
import time
#import pooler
#import copy
from report import report_sxw
#import pdb
#import re
#import locale

class reportes_report_d( report_sxw.rml_parse ):

    def __init__(self,cr,uid,name,context):
        super(reportes_report_d,self).__init__(cr,uid,name,context=context)

        self.localcontext.update({
            'time': time,
            'get_period': self._get_period,
            'get_move': self._get_move      
        })
        
    def _get_period(self, period_id):
        return self.pool.get('account.period').browse(self.cr, self.uid, period_id).name

    
    def _get_move(self, period_list, company_id):
        
        #auxiliares_=''
        debe_=''
        haber_=''
        suma_debe=0
        suma_haber=0                        
    
        if period_list :
            pass
        else :
            today = time.strftime('%Y-%m-%d')
            self.cr.execute ("select id from account_fiscalyear where date_stop > '%s' and date_start < '%s'"%(today,today))
            fy = self.cr.fetchall()
            self.cr.execute ("select id from account_period where fiscalyear_id = %d"%(fy[0][0]))
            periods = self.cr.fetchall()
            for p in periods :
                period_list[0][2].append(p[0])
    
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
                'cuenta': 'Cuenta',
                'glosa': 'Glosa',
                'documento': 'Documento',        
                'debe': 'Debe',    
                'haber': 'Haber',        
                'msilva':'titulos'     
                }               
        invoice_report.append(obj_b)
        #fin titulos
        for period_id in period_list:
            criteria = [('company_id','=',company_id[0]),
                        ('state','=','valid'),   
                        ('period_id','=',period_id)]
            tai_ids_aml = tai_aml.search(self.cr, self.uid, criteria)       
            for each_cuentas in tai_aml.browse(self.cr, self.uid, tai_ids_aml):
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
                        'cuenta': each_cuentas.account_id.code,
                        'glosa': each_cuentas.ref,
                        'documento': each_cuentas.name, 
                        'debe': self.formatLang(debe_,digits = 0),    
                        'haber': self.formatLang(haber_,digits = 0),        
                        'msilva':'data'                                                    
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
                            'msilva':'titulos3'                                                    
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
                            'cuenta': each_cuentas.account_id.code,
                            'glosa': each_cuentas.ref,
                            'documento': each_cuentas.name, 
                            'debe': self.formatLang(debe_,digits = 0),    
                            'haber': self.formatLang(haber_,digits = 0),        
                            'msilva':'data'                                                    
                            }                                                  
                    invoice_report.append(obj_b)               
    
    
    
    
    
    
                    
    
            #no sacar esta line :ref muy IMportanTE
            #retorna sabana para el rml each_cuentas.move_id.x_glosa
        return invoice_report

report_sxw.report_sxw('report.reportes_report_d', 
                      'reportes', 
                      'addons/reportes/reportes_report_d.rml',
                       parser = reportes_report_d, header=False
)
