# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import warnings
from lxml import etree
import openerp.addons.decimal_precision as dp

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _name="account.invoice"
    _inherit="account.invoice"
    
    booleano = False                                                 #Global
    
    def invoice_validate(self, cr, uid, ids, context=None):
        
        campos = self.browse(cr, uid, ids)                           #busco ids de las facturas
        periodo = campos[0]['period_id']['id']                       #dejo en periodos los periodo
        lista = self.search(cr, uid, [('state','!=','draft'),('type','=','in_invoice')])       #traigo ids de todas las fact.
        invoices = self.read(cr, uid, lista)                         #busco las facturas con el periodo
	#boolean = False
        #bloque validador de cuentas analiticas  Descomentar para incluir validacion de cuentas analiticas e incluir account.py
        #codigo pablo 
        #lineas = campos[0].invoice_line
        #line = 1
        #romper = False
        #mensaje = 'Las siguientes lineas de factura requieren cuenta analitica : \n'
        #for ln in lineas:
        #    cuentas_obj = self.pool.get('account.account')
        #    acc_id = ln.account_id.id
        #    acc_campos = cuentas_obj.read(cr, uid, [acc_id])
        #    if acc_campos[0]['user_type'][1].lower() == 'expense' or acc_campos[0]['user_type'][1].lower() == 'income':  
        #       if ln.account_analytic_id:
        #           pass
        #       else:
        #           romper = True
        #           acc_nombre = acc_campos[0]['name']
        #           mensaje += 'linea %d, cuenta : %s \n' % (line, acc_nombre)                        
        #    line +=1       
        
        
        #if romper:
        #    raise osv.except_osv(_('Error!'),_(mensaje))
        
        # Fin codigo Pablo
        #bloque validador de cuentas analiticas
        for i in invoices:              
            if i['partner_id'][0] == campos[0]['partner_id']['id'] and i['reference'] == campos[0]['reference'] and campos[0]['journal_id']['id'] == i['journal_id'][0]:  
                raise osv.except_osv(_('Error!'),_('Proveedor, numero de factura y diarios repetidos! no se validara la factura.'))
            
            
            if i['partner_id'][0] == campos[0]['partner_id']['id'] and i['supplier_invoice_number'] == campos[0]['supplier_invoice_number']:
                if self.booleano:
                    self._topen(cr, uid, ids, context)

                else:
                    self.booleano = True
                    self._message(cr, uid, ids, context)
           # boolean =True
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        
        
    def _topen(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        
    def _message(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Advertencia!'),_('Numero es coincidente con otro tipo de documento! Sin embargo, se validara la factura si vuelve a validar.'))
            
account_invoice()
