from openerp.osv import osv, fields
import time
from datetime import timedelta,date,datetime
from suds.client import Client
from suds import WebFault
import ast
import locale
import httplib
from urlparse import urlparse
import os,sys
import socket
from HTMLParser import HTMLParser
from pyquery import * 

import logging
_logger = logging.getLogger(__name__)

class res_currency_select_automatic_update(osv.osv):
    _inherit = 'res.currency'
    _description = 'Agrega campo para marcar monedas que se actualizan automaticamente'
    _columns = {
        'cod_bcentral': fields.char('Codigo Banco Central de Chile',size=32, required=False), #,('Codigo Banco Central de Chile'),
        'actualizacion_ws': fields.boolean('Actualizar automaticamente'),
    }

    def _carga_tipo_cambio(self,cr,uid,context=None):
       
        namecurrencyrate = time.strftime('%Y-%m-%d')
        DiccionarioTipoCambio = {}

        pq = pyquery.PyQuery
        
        pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx')

        paginados = str((pagina(".verSerie a[id='hypLnk1_11']"))).split('param=')
        urlfinal = 'http://si3.bcentral.cl/Indicadoressiete/secure/ListaSerie.aspx?param=' + paginados[1].replace('">Ver lista</a>&#13;','')
        print urlfinal
        
        pagina = pq(url=urlfinal)
        paginados = (pagina(".filas_lista_series td"))
        nombres=  (str(paginados(".glosa2")).replace('</td>','').replace('&#195;&#169;','e').replace('&#195;&#177;','n').replace('&#195;&#129;','a').replace('&#195;&#179;','o').replace('&#195;&#173;','i').replace('&#195;&#161;','a').replace('&#195;&#186;','u')).split('<td class="glosa2">')
        
        valores =  (str(paginados(".valor")).replace('</td>','')).split('<td class="valor">')
        contador = 0
        for n in nombres:
            DiccionarioTipoCambio[n] = valores[contador].replace('.','').replace(',','.')
            #print n + '=' + valores[contador]
            contador = contador + 1
        
        
        pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx')
        tablatipocambio =  pagina("table .filas_indicadores")
        valordolarobs =  tablatipocambio(".valor label[id='lblValor1_3']").text()
        valoruf =  tablatipocambio(".valor label[id='lblValor1_1']").text()
        DiccionarioTipoCambio['Dolar Observado'] = valordolarobs.replace('.','').replace(',','.')
        DiccionarioTipoCambio['UF'] = valoruf.replace('.','').replace(',','.')
        DiccionarioTipoCambio['CLP'] = valordolarobs.replace('.','').replace(',','.')
        print DiccionarioTipoCambio
        curerncy_ids = self.pool.get('res.currency').search(cr,uid,[('actualizacion_ws','=',True),])
        resultado = self.read(cr, uid, curerncy_ids,['id','name', 'cod_bcentral'])
        
        if not resultado:
            return
             
        for monedas in resultado:
            try:
               
                valordolar = DiccionarioTipoCambio.get("Dolar Observado")
                valoruf = DiccionarioTipoCambio.get("UF")
                paridaduf = str(float(valordolar) / float(valoruf))
               
                if (monedas['cod_bcentral']==None) or (monedas['cod_bcentral']=='') or (monedas['cod_bcentral']==False):
                    print monedas['name'] + ' no tiene definido el codigo del banco central'
                    _logger.warning(monedas['name'] + ' no tiene definido el codigo del banco central')
                else:
                
                    print monedas['name'] + ' ' + 'paso if'
                
                    #TRAE EL VALOR DEL DOLAR PARA CALCULAR LA PARIDAD DEL EURO
                    valordolar = DiccionarioTipoCambio.get("Dolar Observado")
                    valoruf = DiccionarioTipoCambio.get("UF")
                    paridaduf = str(float(valordolar) / float(valoruf))
                    
                    print monedas['name'] + ' ' + 'paso if 2'
                    
                    tipocambio =  DiccionarioTipoCambio.get(monedas['cod_bcentral'])
                    if tipocambio == None:
                        print 'No hay tipo cambio para ' + monedas['name']
                    else:
                        if (monedas['cod_bcentral']=='UF'):
                            tipocambio = paridaduf
                        #tipocambio = tipocambio.replace('.','').replace(',','.')
                        currency_id = monedas['id']
                        objeto_res_currency_rate = self.pool.get('res.currency.rate')
                        
                        result = objeto_res_currency_rate.search(cr,uid,[('currency_id','=',currency_id),('name','=',namecurrencyrate)]) #(cr, uid, [('currency_id','=',currency_id),('name','=',namecurrencyrate)])
                        #print "result"
                        #print result
                        
                                       
            
                        
                        if not result:
                            #print 'No encontro currency rate'
                            objeto_res_currency_rate.create(cr,uid,  {'currency_id': currency_id, 'rate': tipocambio, 'name': namecurrencyrate})
                            #objeto_res_currency_rate.create(cr,uid,  [0,False,{'currency_id': currency_id, 'rate': valordolar, 'name': namecurrencyrate}])
                        else:
                            valorguardado = self.pool.get('res.currency.rate').read(cr, uid,result[0],['rate'])
                            #print "valorguardado"
                            #print valorguardado
                            #print valorguardado['rate']
                           
                            if (float(tipocambio) != float(valorguardado['rate'])):
                                #actualiza el valor
                                #print "es distinto"
                                self.pool.get('res.currency.rate').unlink(cr, uid, valorguardado['id'])
                                objeto_res_currency_rate.create(cr,uid,  {'currency_id': currency_id, 'rate': tipocambio, 'name': namecurrencyrate})
                            else:
                                
                                print 'El valro del dolar es igual al de la base de datos'
                      
            except ValueError:
                print 'Error !"#$!#%!#%!#%$!'
