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

from openerp.osv import osv,fields
#import funcion_bancochile

class res_partner_modLimiteCredito(osv.osv):
    _inherit="res.partner"

    _columns={
              'ref_venta': fields.float('Credito venta', help='Valor de referencia para limite de credito en Ventas.'),
              'ref_arriendo': fields.float('Credito arriendo', help='Valor de referencia para limite de creditos en Arriendos.'),
              'credit_limit': fields.float(string='Limite de credito total'),
              'linea_aprobada': fields.float(string='Total linea aprobada (UF)'),
              'tipo_cliente':fields.char('Tipo de clientes', size = 30),
              'estado_seguro':fields.char('Estado del seguro', size=30),
              'fecha_vigencia':fields.date('Fecha inicio vigencia'),
              'date_credit': fields.date('Vigencia Linea de Credito', required=False),
              }


res_partner_modLimiteCredito()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: