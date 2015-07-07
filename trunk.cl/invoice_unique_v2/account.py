# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class account_account(osv.osv):
    _inherit = "account.account"
    
    TYPE_SELECTION = [
        ('costo', 'Costo'),
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),        
        ('no operacional', 'No Operacional')        
    ]
    _columns = {
                'type_analytic': fields.selection(TYPE_SELECTION, 'Tipo Asociacion Analitica', select=True),
                }
account_account()

class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"
    
    TYPE_SELECTION = [
        ('costo', 'Costo'),
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),        
        ('no operacional', 'No Operacional')        
    ]
    _columns = {
                'type_analytic': fields.selection(TYPE_SELECTION, 'Tipo Resultado Analitica', select=True, required=True),
                }
account_analytic_account()    

class account_move(osv.osv):    
    _inherit = "account.move"
    
    
    def button_validate(self, cursor, user, ids, context=None):
        for move in self.browse(cursor, user, ids, context=context):
            # check that all accounts have the same topmost ancestor
            top_common = None
            for line in move.line_id:
                account = line.account_id
                top_account = account
                while top_account.parent_id:
                    top_account = top_account.parent_id
                if not top_common:
                    top_common = top_account
                elif top_account.id != top_common.id:
                    raise osv.except_osv(_('Error!'),
                                         _('You cannot validate this journal entry because account "%s" does not belong to chart of accounts "%s".') % (account.name, top_common.name))        
        #Validacion cuenta analitica 
        self.validar_cuenta_analitica(cursor, user, ids, context)
        # Fin codigo Pablo
        return self.post(cursor, user, ids, context=context)
    
    def validar_cuenta_analitica(self, cursor, user, ids, context=None):
        linea = 1
        romper = False
        romper_for_type = False
        acc_no_type = False
        acca_no_type = False
        mensaje = 'Las siguientes lineas requieren cuenta analitica: \n'
        mensaje_for_type = 'los campos Tipo Asociacion Analitica y Tipo Resultado Analitica deben ser del mismo tipo\n'
        account_none_type = 'Las siguientes cuentas requieren Campo: Tipo Asociacion Analitica \n'
        analytic_none_type = 'Las siguientes cuentas analyticas requieren Campo: Tipo Resultado Analitica \n'
        mensaje = 'Las siguientes lineas requieren cuenta analitica: \n'
        for move in self.browse(cursor, user, ids, context=context):            
            top_common = None
            for line in move.line_id:
                cuentas_obj = self.pool.get('account.account')
                acc_id = line.account_id.id
                acc_campos = cuentas_obj.read(cursor, user, [acc_id])
                acc_nombre = acc_campos[0]['name']
                if acc_campos[0]['user_type'][1].lower() == 'expense' or acc_campos[0]['user_type'][1].lower() == 'income':  
                    # si no tiene cuenta analiticas las requerimos 
                    if line.analytic_account_id:                        
                        pass
                    else:
                        romper = True                        
                        mensaje += 'Linea %d, Cuenta : %s, requiere campo cuenta analitica \n' % (linea, acc_nombre)                                                        

                if line.analytic_account_id:                        
                        anal_id = line.analytic_account_id['id']
                        bool_type = False
                        bool_none_type = False                        
                        if acc_campos[0]['type_analytic']:                            
                            bool_type,name_analy,type_analy,bool_none_type = self.validar_tipo_analitica(cursor, user, anal_id, acc_campos[0]['type_analytic'], context)                        
                            
                            if bool_none_type:
                                acca_no_type = True
                                analytic_none_type += 'Linea %d, Cuenta : %s \n' % (linea, name_analy)
                            
                            if bool_type:                                                                               
                                romper_for_type = True
                                acc_nombre = acc_campos[0]['name']
                                mensaje_for_type += 'Linea %d, Cuenta : %s, tipo : %s  y Analitica : %s , tipo : %s  \n' % (linea, acc_nombre,acc_campos[0]['type_analytic'],name_analy.lower(),type_analy.lower())                                                    
                        else:
                            acc_no_type = True
                            account_none_type += 'Linea %d, Cuenta : %s \n' % (linea, acc_nombre)
                                    
                linea +=1          
        
        if romper:
            raise osv.except_osv(_('Advertencia!'),_(mensaje))
        
        if acc_no_type:
            raise osv.except_osv(_('Advertencia!'),_(account_none_type))
        
        if acca_no_type:
            raise osv.except_osv(_('Advertencia!'),_(analytic_none_type))
        
        if romper_for_type:
            raise osv.except_osv(_('Advertencia!'),_(mensaje_for_type))
    
    
    def validar_tipo_analitica(self, cursor, user, ids, acc_type, context=None):
        bool_an_distinto = False
        bool_an_dont_type = False
                
        cursor.execute('SELECT type_analytic,name FROM account_analytic_account WHERE id = %d' % ids)
        analytic_type = cursor.fetchall()
                                
        if analytic_type[0][0]:
            print 'Aqui Comparacion'
            print analytic_type[0][0].lower()+"------"+ acc_type                                      
            if analytic_type[0][0].lower() != acc_type:                                
                bool_an_distinto = True
                return bool_an_distinto , analytic_type[0][1],analytic_type[0][0].lower(),bool_an_dont_type
            else:
                return bool_an_distinto , analytic_type[0][1],analytic_type[0][0].lower(),bool_an_dont_type
        else:
            return bool_an_distinto, analytic_type[0][1],analytic_type[0][0].lower(),True
            
account_move()

