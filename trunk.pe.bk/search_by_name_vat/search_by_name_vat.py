# -*- coding: utf-8 -*-
#################################################################################################
#	FICHA DE ACCIDENTES Y SEGUIMIENTO DE ACCIDENTES						#
#			Creado por:								#
#			 	Hugo Herrera (hherrera@stratanet.cl)				#
#				David Acevedo (dacevedo@stratanet.cl)				#
#				Diego Cantos (dcantos@stratanet.cl)				#
#		 	www.stratanet.cl							#
#################################################################################################

from osv import osv, fields
import datetime

class partner_search_name_code_field(osv.osv):

    _inherit="res.partner"

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        try:
            if name and str(name).startswith('partner:'):
                part_id = int(name.split(':')[1])
                part = self.pool.get('res.partner').browse(cr, user, part_id, context=context)
                args += [('id', 'in', (part.property_account_payable.id, part.property_account_receivable.id))]
                name = False
            if name and str(name).startswith('type:'):
                type = name.split(':')[1]
                args += [('type', '=', type)]
                name = False
        except:
            pass
        if name:
            ids = self.search(cr, user, [('name', '=like', "%"+ name +"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('vat', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of account for searching
                operand1,operand2 = name.split(' ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('vat', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'vat'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['vat']:
                name = record['vat'] + ' ' + name
            res.append((record['id'], name))
        return res

partner_search_name_code_field()
