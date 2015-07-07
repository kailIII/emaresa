from osv import osv, fields
#import time
#from datetime import datetime

import logging
_logger = logging.getLogger('reportes')

class reportes(osv.osv_memory):
	_name = 'reportes'
	_columns = {   
		'compania': fields.many2one('res.company', 'Empresa', required=True),
		'periodos': fields.many2many('account.period', 'vat_period_rel', 'vat_id', 'period_id', 'Periodo`s', help="Seleccione el o los Periodos"),
		'si': fields.boolean('S.I.I.', help="Activa - Genera reportes para hojas timbradas por S.I.I."),	
		'type_': fields.selection([('Balance Tributario', 'Balance Tributario'), ('Libro de Compras', 'Libro de Compras'), ('Libro de Ventas', 'Libro de Ventas'), ('Libro Diario', 'Libro Diario'),('Libro Honorarios','Libro Honorarios')], 'Reporte')
		}
			
	def create_report(self, cr, uid, ids, context=None):
		
		#data = self.read(cr,uid,ids,)
		#print data,' create_report('
		#_logger.info("*********************************************")
		#_logger.info("data " +str(data))
		#_logger.info("*********************************************")
		
		
		data = self.read(cr,uid,ids,)[-1]

		#_logger.info("*********************************************")
		#_logger.info("data [-1]" +str(data))
		#_logger.info("*********************************************")


		
		if self.browse(cr, uid, ids)[0].type_=="Libro de Ventas":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'reportes_print_libven',
				'datas': {
					'model':'reportes',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
		if self.browse(cr, uid, ids)[0].type_=="Libro de Compras":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'reportes_print_libcom',
				'datas': {
					'model':'reportes',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}		
		if self.browse(cr, uid, ids)[0].type_=="Balance Tributario":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'reportes_print_baltri',
				'datas': {
					'model':'reportes',
					'id': context.get('active_ids') and context.get('active_ids')[0] or False,
					'ids': context.get('active_ids') and context.get('active_ids') or [],
					'form':data
							},
						'nodestroy': False
				}
			
		if self.browse(cr, uid, ids)[0].type_=="Libro Diario":
			return {
				'type'         : 'ir.actions.report.xml',
				'report_name'   : 'reportes_report_d',
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
reportes()
