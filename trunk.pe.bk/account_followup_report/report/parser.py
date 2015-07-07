import time, datetime
from collections import defaultdict
from openerp import pooler
from report import report_sxw
#import logging
#_logger = logging.getLogger(__name__)

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(Parser, self).__init__(cr, uid, name, context=context)

		self.tots = [ 0, 0, 0, 0, 0 ]
		self.lineas = {}
		self.lista = []

		self.localcontext.update({
			'time': time,
			'ids_to_objects': self._ids_to_objects,
			'get_lines': self._lines_get,
			'get_text': self._get_text,
			'dias': self.dias,
			'saldos': self.saldos,
			'saldosHasta': self.saldosHasta,
			'total': self.total,
			'centroCosto': self.costos,
			'formatRut': self.formatRut,
			'get_journals': self.get_journals,
			'agrupados': self.agrupados,
		})

	def get_journals(self):
		return self.lista

	def agrupados(self, journal):
		agrupa = []
		for linea in self.lineas[journal]:
			if linea['journal'] == journal:
				agrupa.append(linea)
		return agrupa

	def _ids_to_objects(self, ids):
		pool = pooler.get_pool(self.cr.dbname)
		all_lines = []
		for line in pool.get('account_followup.stat.by.partner').browse(self.cr, self.uid, ids):
			if line not in all_lines:
				all_lines.append(line)
		return all_lines

	def _lines_get(self, stat_by_partner_line):
		self.lineas = self._lines_get_with_partner(stat_by_partner_line.partner_id, stat_by_partner_line.company_id.id)
		journal = ''
		for aux in self.lineas.values():
			for linea in aux:
				if journal != linea['journal']:
					self.lista.append(linea['journal'])
				journal = linea['journal']
		return True

	def _nombres(self, journal, name):
		if journal == 'DIARIO DE APERTURA':
			if name.find('ABO-SALDO') != -1:
				return 'ABONO'
			elif name.find('N_CRED_VEN') != -1:
				return 'NOTA DE CREDITO VENTA'
			elif name.find('N_CRED_ARR') != -1:
				return 'NOTA DE CREDITO ARRIENDO'
			elif name.find('CHE_XCOB') != -1:
				return 'CHEQUE POR COBRAR'
			elif name.find('CUOT_COB') != -1:
				return 'FACTURA'
			elif name.find('CAR-CARGO') != -1:
				return 'CARGO'
			elif name.find('FAC_EXPORT') != -1:
				return 'FACTURA DE EXPORTACION'
			elif name.find('INT_COB') != -1:
				return 'INTERESES POR COBRAR'
			elif name.find('PAG_CART') != -1:
				return 'PAGARE EN CARTERA'
		elif journal.find('FACTURA') != -1:
			return 'FACTURA'
		elif journal.find('DE CREDITO') != -1:
			return 'NOTA DE CREDITO'
		elif journal.find('CANJE PROVEEDORES') != -1 or journal.find('CANJE CLIENTES') != -1 or journal.find('TRANSFERENCIA') != -1:
			return 'ABONO'

		return journal

	def _lines_get_with_partner(self, partner, company_id):
		pool = pooler.get_pool(self.cr.dbname)
		moveline_obj = pool.get('account.move.line')
		moveline_ids = moveline_obj.search(self.cr, self.uid, [
								('partner_id', '=', partner.id),
								('account_id.type', '=', 'receivable'),
								('reconcile_id', '=', False),
								('state', '!=', 'draft'),
								('company_id', '=', company_id),
								'|',('reconcile_partial_id', '=', False),
								('debit', '>', 0)
							],
							order='date_maturity, journal_id, ref')
		move_line_obj = moveline_obj.browse(self.cr, self.uid, moveline_ids)
		lines_per_journal = defaultdict(list)

		for line in move_line_obj:
			invoice_number = ''
			if line.journal_id.name.find('DE CREDITO') != -1:
	 			invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('move_id','=',line.move_id.id)])
				if invoice_ids:
					invoice_number = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids)[0].invoice_number

			if line.journal_id.name.find('DE CREDITO') != -1:
				line_name = invoice_number
			elif line.journal_id.code in ['466', '520', '521']:
				line_name = line.name
			else:
				line_name = line.ref
			currency = line.currency_id or line.company_id.currency_id

			line_data = {
				'id': line.id,
				'name':	line_name,
				'ref': line.ref,
				'date': line.date,
				'date_maturity': line.date_maturity or line.date,
				'type': self._nombres(line.journal_id.name, line.name),
				'journal': line.journal_id.name,
				'balance': line.amount_currency if currency != line.company_id.currency_id else line.debit - line.credit,
				'blocked': line.blocked,
				'currency': line.currency_id.name or line.company_id.currency_id.name,
				'move_id': line.move_id.id
			}
			lines_per_journal[line_data['journal']].append(line_data)

		return lines_per_journal

	def _get_text(self, stat_line, followup_id, context=None):
		if context is None:
			context = {}
		context.update({'lang': stat_line.partner_id.lang})
		fp_obj = pooler.get_pool(self.cr.dbname).get('account_followup.followup')
		fp_line = fp_obj.browse(self.cr, self.uid, followup_id, context=context).followup_line
		if not fp_line:
			raise osv.except_osv(_('Error!'),_("The followup plan defined for the current company does not have any followup action."))
		#the default text will be the first fp_line in the sequence with a description.
		default_text = ''
		li_delay = []
		for line in fp_line:
			if not default_text and line.description:
				default_text = line.description
			li_delay.append(line.delay)
		li_delay.sort(reverse=True)
		a = {}
		#look into the lines of the partner that already have a followup level, and take the description of the higher level for which 
		#it is available
		partner_line_ids = pooler.get_pool(self.cr.dbname).get('account.move.line').search(self.cr, self.uid,\
							[('partner_id','=',stat_line.partner_id.id),('reconcile_id','=',False),\
							('company_id','=',stat_line.company_id.id),('blocked','=',False),\
							('state','!=','draft'),('debit','!=',False),('account_id.type','=','receivable'),\
							('followup_line_id','!=',False)])
		partner_max_delay = 0
		partner_max_text = ''
		for i in pooler.get_pool(self.cr.dbname).get('account.move.line').browse(self.cr, self.uid, partner_line_ids, context=context):
			if i.followup_line_id.delay > partner_max_delay and i.followup_line_id.description:
				partner_max_delay = i.followup_line_id.delay
				partner_max_text = i.followup_line_id.description
		text = partner_max_delay and partner_max_text or default_text
		if text:
			text = text % {
					'partner_name': stat_line.partner_id.name,
					'date': time.strftime('%Y-%m-%d'),
					'company_name': stat_line.company_id.name,
					'user_signature': pooler.get_pool(self.cr.dbname).get('res.users').browse(self.cr,\
						self.uid, self.uid, context).signature or '',
			}
		return text		

	def dias(self, hoy, venc):
		if venc:
			dias = datetime.datetime.strptime(hoy, '%Y-%m-%d').date() - datetime.datetime.strptime(venc, '%Y-%m-%d').date()
			return dias.days
		else:
			return ''

	def saldos(self, line_id, balance):
		credit = 0
		debit = 0
		line = self.pool.get('account.move.line').browse(self.cr, self.uid, line_id)
		if line.reconcile_partial_id:
			partial_ids = self.pool.get('account.move.line').search(self.cr, self.uid,\
								[('reconcile_partial_id', '=', line.reconcile_partial_id.id)])
			if partial_ids:
				partial_objs = self.pool.get('account.move.line').browse(self.cr, self.uid, partial_ids)
				for partial in partial_objs:
					credit += partial.credit
					debit += partial.debit
				return float(debit - credit)
		return float(balance)
		
	def saldosHasta(self, hoy, venc, line_id, balance, opc):
		saldo = self.saldos(line_id, balance)
		if opc == 0:
			self.tots[opc] += balance
			return self.formatLang(balance, digits=0)
		if venc:
			dias = self.dias(hoy, venc)
			if opc == 1 and dias > 60:
				self.tots[opc] += saldo
				return self.formatLang(saldo, digits=0)
			elif opc == 2 and dias <= 60 and dias >= 31:
				self.tots[opc] += saldo
				return self.formatLang(saldo, digits=0)
			elif opc == 3 and dias <= 30 and dias >= 0:
				self.tots[opc] += saldo
				return self.formatLang(saldo, digits=0)
			elif opc == 4 and dias < 0:
				self.tots[opc] += saldo
				return self.formatLang(saldo, digits=0)
			else:
				''
		else:
			return ''

	def total(self, opc):
		if opc == 0:
			return self.formatLang(self.tots[opc], digits=0)
		elif opc == 1:
			return self.formatLang(self.tots[opc], digits=0)
		elif opc == 2:
			return self.formatLang(self.tots[opc], digits=0)
		elif opc == 3:
			return self.formatLang(self.tots[opc], digits=0)
		elif opc == 4:
			return self.formatLang(self.tots[opc], digits=0)
		else:
			return ''

	def costos(self, move_id):
		cc = ''
		amount = 0
		line_ids = self.pool.get('account.move.line').search(self.cr, self.uid, [('move_id', '=', move_id)])
		line_obj = self.pool.get('account.move.line').browse(self.cr, self.uid, line_ids)
		for line in line_obj:
			if line.journal_id.name == 'DIARIO DE APERTURA':
				return line.centro_costo		

				ids_cc = self.pool.get('account.move.line').search(self.cr, self.uid,\
									['|',('reconcile_id', '=', line.reconcile_id),\
									('reconcile_partial_id', '=', line.reconcile_partial_id)])
				if ids_cc:
					for id_cc in ids_cc:
						if id_cc in line_ids:
							ids_cc.pop(ids_cc.index(id_cc))

					objs = self.pool.get('account.move.line').browse(self.cr, self.uid, ids_cc)


					obj_cc = self.pool.get('account.analytic.line').browse(self.cr, self.uid, ids_cc)
					for line in obj_cc:
						if abs(line.amount) > amount:
							cc = str(line.account_id.code)
							amount = abs(line.amount)
					return cc
#					return self.pool.get('res_users').browse(cr, uid, uid).codecc
				
		analytic_ids = self.pool.get('account.analytic.line').search(self.cr, self.uid, [('move_id', 'in', line_ids)])
		if analytic_ids:
			objs = self.pool.get('account.analytic.line').browse(self.cr, self.uid, analytic_ids)
			for line in objs:
				if abs(line.amount) > amount:
					cc = str(line.account_id.code)
					amount = abs(line.amount)
			return cc
		else:
			return 'S/CC'

	def formatRut(self, rut):
		if rut:
			return rut[2:-7]+'.'+rut[-7:-4]+'.'+rut[-4:-1]+'-'+rut[-1:]

report_sxw.report_sxw('report.followup_cta_cte_report', 'account_followup.followup',\
			'account_followup_report/report/template_cta_cte.rml', parser=Parser, header=False)

report_sxw.report_sxw('report.followup_cta_cte_without_header_report', 'account_followup.followup',\
			'account_followup_report/report/template_cta_cte_without_header.rml', parser=Parser, header=False)

