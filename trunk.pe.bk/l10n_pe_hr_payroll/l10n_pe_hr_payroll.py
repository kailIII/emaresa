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
from osv import fields,osv




class rem_afp(osv.osv):
    """Class AFP"""
    _name = 'rem.afp'
    def _Total_afp (self, cr, uid, ids, field_name, arg, context=None):
        if not ids: return()
        res = {}
        for o in self.browse (cr, uid, ids):
            res[o.id] = o.commission + o.contribution + o.SIS
        return res
    _columns = {
        'name': fields.char('Name', size=50, required=True, translate=True),
        'commission': fields.float('Comision Flujo', size=6, required=True,),
        'commission2': fields.float('Comision Mixta', size=6, required=True,),
        'contribution': fields.float('Fondo', size=6, required=True,),
        'SIS': fields.float('SEG', size=6, required=True,),
        'tope': fields.float('Tope', size=10, required=True,),
        'comision_tope': fields.float('Comision Tope S/.', size=6, required=True,),
        'employee_ids': fields.one2many('hr.employee', 'afp_id',string='Employees'),
        'cod_previred': fields.char('Codigo', size=10),
        'Total_AFP': fields.function(_Total_afp, method=True, type='float', string='Total AFP'),
    }
rem_afp()

class hr_employee(osv.osv):
    """Update employee class"""
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _columns = {
        'afp_id': fields.many2one('rem.afp',string='AFP', required=True,),
        'health_ids': fields.many2one('rem.health', string='health'),
        'total_afp': fields.float('Total_AFP', size=6, required=True),
        'codigo': fields.char('Código', size=16),
        'no_cusp': fields.char('No C.U.S.P.', size=16),
        'currency': fields.many2one('res.currency'),
        'indicator': fields.many2one('rem.indicator', 'Conceptos Remunerativos y No Remunerativos'),
        'voluntary_saving_ids': fields.many2one('rem.voluntary_saving', string='Entidades Prestadoras de Salud'),
        'rem_neto_id': fields.many2one('rem.neto', string='Retencion'),
        'tiempos_id': fields.many2one('rem.tiempos', string='Tiempos'),
        'adelantos_id': fields.many2one('rem.adelantos', string='Adelantos'),
        'tax_segment_id': fields.many2one('rem.tax_segment',string='Impuesto 5ta. categoria'),
        'type_commis': fields.selection([('Mixta','M'),('Flujo','F')],'Tipo Comisión'),
        
    }
   
hr_employee()

class rem_health(osv.osv):
    """Health"""
    _name = 'rem.health'
    _columns = {
        'name': fields.char('Name', size=16),
        'tax_cap': fields.float('tax_cap', size=4, required=True,),
        'employee_ids': fields.one2many('hr.employee', 'health_ids',string='Employees'),
    }
rem_health()

class rem_neto(osv.osv):
    """Retencion"""
    _name = 'rem.neto'
    _columns = {
        'name': fields.char('Name', size=50),
        'period_id': fields.many2one('account.period', string='Periodo',),
        'employee_ids': fields.many2one('hr.employee',string='Empleados'),
        'monto_neto': fields.float('Retencion', size=16),
    }
rem_neto()

class rem_tax_segment(osv.osv):
    """Tax Segment"""
    _name = 'rem.tax_segment'
    _columns = {
        'ini_segment': fields.float('ini_segment', size= 10,),
        'end_segment': fields.float('end_segment', size= 10,),
        'tax': fields.float('tax', size=6,),
        'descto': fields.float('tramo_dscto', size=6,),
        'name':fields.text('Nombre'),
        'UIT1':fields.float('UIT1', size=6),
        'UIT2':fields.float('UIT2', size=6),
        'UIT3':fields.float('UIT3', size=6),
        'UIT4':fields.float('UIT4', size=6),
        'employee_ids': fields.one2many('hr.employee', 'tax_segment_id',string='Empleados'),
    }
rem_tax_segment()

class rem_indicator(osv.osv):
    """Concep. Rem y No Rem"""
    _name = 'rem.indicator'
    _columns = {
        'name': fields.char('Nombre', size=50),
        'asig_fam': fields.float('Asignacion Familiar', size=10, required=True,),
        'comisiones': fields.float('Comisiones', size=10, required=True,),
#        'hr_ext': fields.float('Horas Extra', size=10, required=True,), #### Va a depender de la forma que quieran llevar las horas extra, como concepto remunerativo o como tiempos del empleado##
        'vacac': fields.float('Vacaciones', size=10, required=True,),
        'gratif': fields.float('Gratificaciones', size=10, required=True,),
        'bonific2': fields.float('Bonificaciones', size=10, required=True,),
        'bonos': fields.float('Bonos', size=10, required=True,),
        'refrigerio': fields.float('Refrigerio', size=10, required=True,),
        'bonific': fields.float('Bonificacion', size=10, required=True,),
        'cts': fields.float('CTS', size=10, required=True,),
        'otros': fields.float('Otros', size=10, required=True,),
        'employee_ids': fields.one2many('hr.employee', 'indicator',string='Empleados'),
    }
rem_indicator()

class rem_tiempos(osv.osv):
    """Tiempos"""
    _name = 'rem.tiempos'
    _columns = {
        'name': fields.char('Nombre', size=50),
        'diasmes': fields.float('Dias considerados', size=10, required=True,),
        'dias_trab': fields.float('Dias trabajados', size=10, required=True,),
        'trab_real': fields.float('Dias reales trabajados', size=10, required=True,),
        'hrs_trab': fields.float('Horas Trabajadas', size=10, required=True,),
        'hrs_ext': fields.float('Cantidad de Horas Extra', size=10, required=True,),
        'fact_he': fields.float('Factor Horas Extra', size=10, required=True,),
        'employee_ids': fields.one2many('hr.employee', 'tiempos_id',string='Empleados'),
    }
rem_tiempos()

class rem_adelantos(osv.osv):
    """Adelantos"""
    _name = 'rem.adelantos'
    _columns = {
        'name': fields.char('Nombre', size=50),
        'otros': fields.float('Otros', size=50, required=True,),
        'adelantos': fields.float('Adelantos', size=50, required=True,),
        'dep_cts': fields.float('Deposito CTS', size=50, required=True,),
        'quincena': fields.float('Quincena', size=50, required=True,),
        'employee_ids': fields.one2many('hr.employee', 'adelantos_id',string='Empleados'),
    }
rem_adelantos()


class rem_voluntary_saving(osv.osv):
    """Entidades Prestadoras de Salud"""
    _name = 'rem.voluntary_saving'
    _columns = {
        'name': fields.char('Decription EPS', size=50, required=True,),
        'Value': fields.float('Monto', size=12, required=True,),
        'currency': fields.many2one('res.currency', string='Moneda'),
        'Star_Date': fields.date('Fecha Inicio'),
#        'afp_id': fields.many2one('rem.afp',string='AFP'),
        'employee_ids': fields.many2one('hr.employee', string='Empleados'),
    }
rem_voluntary_saving()



