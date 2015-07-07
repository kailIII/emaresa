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

from osv import osv, fields

class reportes_tributarios(osv.osv_memory):
	_name = 'reportes.tributarios'
	_columns = {   
		'company_id':fields.many2one('res.company', 'Empresa', required=True),
		'periodos':fields.many2many('account.period', 'vat_period_rel', 'vat_id', 'period_id', 'Periodo`s',\
				help="Seleccione el o los Periodos"),
		'si':fields.boolean('S.I.I.', help="Activa - Genera reportes para hojas timbradas por S.I.I."),	
		'type_':fields.selection([('Balance Tributario', 'Balance Tributario'),\
					('Libro de Compras', 'Libro de Compras'),\
					('Libro de Ventas', 'Libro de Ventas'),\
					('Libro Diario', 'Libro Diario')], 'Reporte')
		}

	_defaults = {
		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr,\
						uid, 'reportes_tributarios', context=c)
	}
			
	def create_report(self, cr, uid, ids, context=None):
		data = self.read(cr,uid,ids,)[-1]

		if self.browse(cr, uid, ids)[0].type_ == "Libro de Ventas":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'libro_venta_rml',
				'datas': {
					'model':'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
		if self.browse(cr, uid, ids)[0].type_=="Libro de Compras":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'libro_compra_rml',
				'datas': {
					'model':'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}		
		if self.browse(cr, uid, ids)[0].type_=="Balance Tributario":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'balance_tributario_rml',
				'datas': {
					'model':'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
			
		if self.browse(cr, uid, ids)[0].type_=="Libro Diario":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'libro_diario_rml',
				'datas': {
					'model':'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
			
		if self.browse(cr, uid, ids)[0].type_=="Libro Honorarios":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'reportes_libro_honorarios',
				'datas': {
					'model':'reportes',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}

	def create_report_excel(self, cr, uid, ids, context=None):
		data = self.read(cr,uid,ids,)[-1]

		if self.browse(cr, uid, ids)[0].type_ == "Libro de Ventas":
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'libro_venta_xls',
				'datas': {
					'model': 'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
				},
				'nodestroy': False
			}

		if self.browse(cr, uid, ids)[0].type_=="Libro de Compras":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'libro_compra_xls',
				'datas': {
					'model':'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}		
		if self.browse(cr, uid, ids)[0].type_=="Balance Tributario":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'balance_tributario_xls',
				'datas': {
					'model':'reportes.tributarios',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
			
		if self.browse(cr, uid, ids)[0].type_=="Libro Diario":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'libro_diario_xls',
				'datas': {
					'model':'reportes',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
			
		if self.browse(cr, uid, ids)[0].type_=="Libro Honorarios":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'reportes_libro_honorarios',
				'datas': {
					'model':'reportes',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
reportes_tributarios()

class libro_mayor(osv.osv_memory):
    _inherit = "account.report.general.ledger"

    def print_excel(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'amount_currency', 'sortby'])[0])

        if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})


        return { 'type': 'ir.actions.report.xml', 'report_name': 'libro_mayor_xls', 'datas': data}


libro_mayor()

class perdida_ganancia(osv.osv_memory):
    _inherit = "accounting.report"

    def check_report_xls(self, cr, uid, ids, context=None):
    	if context is None:
            context = {}
        
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))

        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'date_to_cmp',  'fiscalyear_id_cmp', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter','target_move'], context=context)[0])
       
        aux = {}
        aux['form'] = self.read(cr, uid, ids, ['account_report_id', 'date_from_cmp',  'date_to_cmp',  'fiscalyear_id_cmp', 'journal_ids', 'period_from_cmp', 'period_to_cmp',  'filter_cmp',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id_cmp', 'chart_account_id', 'period_from_cmp', 'period_to_cmp', 'account_report_id']:
            if isinstance(aux['form'][field], tuple):
                aux['form'][field] = aux['form'][field][0]
        comparison_context = self._build_comparison_context(cr, uid, ids, aux, context=context)
        
        data['form']['comparison_context'] = comparison_context

        return { 'type': 'ir.actions.report.xml', 'report_name': 'account.financial.report.xls', 'datas': data}

perdida_ganancia()

class balance_trece(osv.osv_memory):
	_inherit = "wizard.report"

	def print_report_xls(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
            
		data = {}
		data['ids'] = context.get('active_ids', [])
		data['model'] = context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(cr, uid, ids[0])

		if data['form']['filter'] == 'byperiod':
			del data['form']['date_from']
			del data['form']['date_to']

			data['form']['periods'] = self.period_span(cr, uid, data['form']['periods'], data['form']['fiscalyear'])

		elif data['form']['filter'] == 'bydate':
			self._check_date(cr, uid, data)
			del data['form']['periods']
		elif data['form']['filter'] == 'none':
			del data['form']['date_from']
			del data['form']['date_to']
			del data['form']['periods']
		else:
			self._check_date(cr, uid, data)
			lis2 = str(data['form']['periods']).replace("[","(").replace("]",")")
			sqlmm = """select min(p.date_start) as inicio, max(p.date_stop) as fin 
			from account_period p 
			where p.id in %s"""%lis2
			cr.execute(sqlmm)
			minmax = cr.dictfetchall()
			if minmax:
				if (data['form']['date_to'] < minmax[0]['inicio']) or (data['form']['date_from'] > minmax[0]['fin']):
					raise osv.except_osv(_('Error !'),_('La interseccion entre el periodo y fecha es vacio'))
        
		if data['form']['columns'] == 'one':
			name = 'afr.1cols'
			raise osv.except_osv('Atencion !','Este reporte no esta disponible en Excel.')
		if data['form']['columns'] == 'two':
			name = 'afr.2cols'
			raise osv.except_osv('Atencion !','Este reporte no esta disponible en Excel.')
		if data['form']['columns'] == 'four':
			if data['form']['analytic_ledger'] and data['form']['inf_type'] == 'BS':
				name = 'afr.analytic.ledger'
				raise osv.except_osv('Atencion !','Este reporte no esta disponible en Excel.')
			else:
				name = 'afr.4cols'
				raise osv.except_osv('Atencion !','Este reporte no esta disponible en Excel.')
		if data['form']['columns'] == 'five':
			name = 'afr.5cols'
			raise osv.except_osv('Atencion !','Este reporte no esta disponible en Excel.')
		if data['form']['columns'] == 'qtr':
			name = 'afr.qtrcols'
			raise osv.except_osv('Atencion !','Este reporte no esta disponible en Excel.')
		if data['form']['columns'] == 'thirteen':
			name = 'balance_trece'
        
		return {'type': 'ir.actions.report.xml', 'report_name': name, 'datas': data}

balance_trece()

