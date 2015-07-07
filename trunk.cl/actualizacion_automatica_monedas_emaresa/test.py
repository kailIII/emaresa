#from suds.client import Client
#from suds import WebFault
#import ast

#wsdl = 'http://localhost:8080/PruebaEconube/PruebaEconube?wsdl'
#name = ' Nelson Diaz Navarro'

        
        

#wsdl = 'http://localhost:8080/PruebaEconube/PruebaEconube?wsdl'
#name = ' Nelson Diaz Navarro'
#leer todos los ids de los tipos de cambio que se quieren actualizar
#curerncy_ids = self.pool.get('res.currency').search(cr,uid,[('actualizacion_ws','=',True),])
#client = Client(wsdl)



import httplib
from urlparse import urlparse
import os,sys
import socket

class html(object):
    
    def __init__(self):
        #pass
        self.html_connect("http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_CAD&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBfAGIANABLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=")

    """
    Funcion que realiza la conexion.
    Tiene que recibir: la url
    """
    def html_connect(self,url):
        socket.setdefaulttimeout(20)
        try:
            parse=urlparse(url)
            if parse.scheme=="http":
                #self.conn=httplib.HTTPConnection(parse.netloc,timeout=60)
                self.conn=httplib.HTTPConnection(parse.netloc)
            else:
                #self.conn=httplib.HTTPSConnection(parse.netloc,timeout=60)
                self.conn=httplib.HTTPSConnection(parse.netloc)
            if parse.path=="":
                # Si no disponemos de path le ponemos la barra
                path="/"
            elif parse.query:
                # Si disponemos de path y query, realizamos el montaje
                path="%s?%s" % (parse.path,parse.query)
            else:
                # Si solo disponemos de path
                path=parse.path
            self.conn.request("GET",path)
            self.response1=self.conn.getresponse()
            self.status=self.response1.status
            self.reason=self.response1.reason
            self.headers=self.response1.getheaders()
        except socket.error:
            #errno, errstr = sys.exc_info()[:2]
            #if errno == socket.timeout:
                #print "There was a timeout"
            #else:
                #print "There was some other socket error"
            self.status=408
        except:
            self.status=404

    """Muestra el estado"""
    def html_showStatus(self):
        try:
            return self.status, self.reason
        except:
            return ""

    """Lee el contenido"""
    def html_read(self):
        self.read1=self.response1.read()

    """Muestra el contenido"""
    def html_showHTML(self):
        if self.read1:
            return self.read1
        return ""

    """Cierra la conexion"""
    def html_close(self):
        try:
            self.conn.close()
        except:
            pass

if __name__=="__main__":
    obj=html()
    if len(os.sys.argv)==3:
        """ Tiene que recibir la pagina a descargar y la opcion 1|2 """
        if os.sys.argv[2]=="1":
            obj.html_connect(os.sys.argv[1])
            print obj.status
        elif os.sys.argv[2]=="2":
            obj.html_connect(os.sys.argv[1])
            obj.html_read()
            print obj.html_showHTML()
    else:
        obj.html_connect("http://si3.bcentral.cl/Indicadoressiete/secure/Serie.aspx?gcode=PAR_CAD&param=dQBoAHMAOABpAGgAMQB2AC4ALQBDAF8AdgBkAFIAUgBWAF8AbQB6AFgAOQBOAGIATgBwAEoAMQBNAE0ARAAuAGQAaQBmADMAUgBtAEsAMQBfAGIANABLADYAMwBDAHkAaQBQAFIARQBBAHMAaQBrAE8AZQBUAHoASQBLAEIALgB3AHkAYQBrAGUAWAB5AFcAZABBADcAVgBNADgAQgA0ADkAYwBsAFkAWgBIAG0ALgB1AFkAUQA=")
        print obj.html_showStatus()
        print obj.status
        print obj.headers
        if obj.status==200:
            obj.html_read()
            print obj.html_showHTML()
    obj.html_close()

