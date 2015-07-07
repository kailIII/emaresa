from pyquery import * 
import time
from datetime import timedelta,date,datetime
'''
namecurrencyrate = time.strftime('%Y-%m-%d')
dia = str(int(time.strftime('%d')) + 1) 

mesnumero = time.strftime('%m')
mestexto = ''

if mesnumero == '01':
    mestexto = "Enero"
elif mesnumero == '02':
    mestexto = "Febrero"
elif mesnumero == '03':
    mestexto = "Marzo"
elif  mesnumero == '04':
    mestexto = "Abril"
elif  mesnumero == '05':
    mestexto = "Mayo"
elif mesnumero == '06':
    mestexto = "Junio"
elif mesnumero == '07':
    mestexto = "Julio"
elif  mesnumero == '08':
    mestexto = "Agosto"
elif  mesnumero == '09':
    mestexto = "Septiembre"
elif mesnumero == '10':
    mestexto = "Octubre"
elif mesnumero == '11':
    mestexto = "Noviembre"
elif  mesnumero == '12':
    mestexto = "Diciembre"
print 'mestexto'

print mestexto

filtrofecha = 'gr_ctl' + dia + '_' + mestexto
print 'filtrofecha'
print filtrofecha

'''
DiccionarioTipoCambio = {}

pq = pyquery.PyQuery



pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx')

paginados = str((pagina(".verSerie a[id='hypLnk1_11']"))).split('param=')
urlfinal = 'http://si3.bcentral.cl/Indicadoressiete/secure/ListaSerie.aspx?param=' + paginados[1].replace('">Ver lista</a>&#13;','')
print urlfinal

pagina = pq(url=urlfinal)
print pagina
paginados = (pagina(".filas_lista_series td"))
nombres=  (str(paginados(".glosa2")).replace('</td>','').replace('&#195;&#169;','e').replace('&#195;&#177;','n').replace('&#195;&#129;','a').replace('&#195;&#179;','o').replace('&#195;&#173;','i').replace('&#195;&#161;','a').replace('&#195;&#186;','u')).split('<td class="glosa2">')
valores =  (str(paginados(".valor")).replace('</td>','')).split('<td class="valor">')
contador = 0
for n in nombres:
    DiccionarioTipoCambio[n] = valores[contador].replace('.','').replace(',','.')
    print n 
    contador = contador + 1


pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx')
tablatipocambio =  pagina("table .filas_indicadores")
valordolarobs =  tablatipocambio(".valor label[id='lblValor1_3']").text()
valoruf =  tablatipocambio(".valor label[id='lblValor1_1']").text()

#print valordolarobs.replace('.','').replace(',','.')
#print valoruf.replace('.','').replace(',','.')
DiccionarioTipoCambio['Dolar Observado'] = valordolarobs.replace('.','').replace(',','.')
DiccionarioTipoCambio['UF'] = valoruf.replace('.','').replace(',','.')
#print DiccionarioTipoCambio

print DiccionarioTipoCambio

'''

pq = pyquery.PyQuery
pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PRE_TCO&param=RABmAFYAWQB3AGYAaQBuAEkALQAzADUAbgBNAGgAaAAkADUAVwBQAC4AbQBYADAARwBOAGUAYwBjACMAQQBaAHAARgBhAGcAUABTAGUAdwA1ADQAMQA0AE0AawBLAF8AdQBDACQASABzAG0AXwA2AHQAawBvAFcAZwBKAEwAegBzAF8AbgBMAHIAYgBDAC4ARQA3AFUAVwB4AFIAWQBhAEEAOABkAHkAZwAxAEEARAA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor dolar observado' + ' ' + tablatipocambio

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PRE_EUR&param=cgBnAE8AOQBlAGcAIwBiAFUALQBsAEcAYgBOAEkASQBCAEcAegBFAFkAeABkADgASAA2AG8AdgB2AFMAUgBYADIAQwBzAEEARQBMAG8ASgBWADQATABrAGQAZAB1ADIAeQBBAFAAZwBhADIAbABWAHcAXwBXAGgATAAkAFIAVAB1AEIAbAB3AFoAdQBRAFgAZwA5AHgAdgAwACQATwBZADcAMwAuAGIARwBFAFIASwAuAHQA')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor euro' + ' ' + tablatipocambio
#datostexto =  datospagina.text()
#print datostexto

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=UF&param=RABmAFYAWQB3AGYAaQBuAEkALQAzADUAbgBNAGgAaAAkADUAVwBQAC4AbQBYADAARwBOAGUAYwBjACMAQQBaAHAARgBhAGcAUABTAGUAYwBsAEMAMQA0AE0AawBLAF8AdQBDACQASABzAG0AXwA2AHQAawBvAFcAZwBKAEwAegBzAF8AbgBMAHIAYgBDAC4ARQA3AFUAVwB4AFIAWQBhAEEAOABkAHkAZwAxAEEARAA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor uf' + ' ' + tablatipocambio

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_SEK&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBWAEMAagBLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor corona sueca' + ' ' + tablatipocambio

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_AUD&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBjAFgANABLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor dolar autraliano' + ' ' + tablatipocambio

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_CHF&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBfAEEAZwBLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor Franco Suizo' + ' ' + tablatipocambio


pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_GBP&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBnAFQARgBLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor Libra esterlina' + ' ' + tablatipocambio

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_JPY&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBqADMAUwBLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor Yen Japones' + ' ' + tablatipocambio

pagina = pq(url='http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_CAD&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBfAGIANABLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=')
tablatipocambio =  pagina(".obs[id='" + filtrofecha + "']").text()#,span.gr_ctl02_Abril").f
print 'valor YDolar Canadience' + ' ' + tablatipocambio



datosseparados = datostexto.split(' ')
print datosseparados[2].replace('.','').replace(',','.')       #dolar observado
print datosseparados[4].replace('.','').replace(',','.')       #euro
print datosseparados[6].replace('.','').replace(',','.')       #uf
print datosseparados[8].replace('.','').replace(',','.')       #utm

'''