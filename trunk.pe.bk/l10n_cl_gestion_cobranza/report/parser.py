import datetime
from report import report_sxw

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.cr = cr
		self.uid = uid
		self.model = ''
		
		self.localcontext.update({
			'principal': self.principal,
			'fecha_documento': self.fecha_documento,
			'periodo': self.periodo,
			'descripcion': self.descripcion,
			'formatRut': self.formatRut,
			'suma': self.suma,
			'get_create_date': self.get_create_date,
			'get_create_uid': self.get_create_uid,
			'dates': self.dates,
			'informacion': self.informacion,
			'get_model': self.get_model
		})

	def principal(self, objects):
		ids = []

		for obj in objects:
			ids.append(obj.move_id.id)

		if obj:
			voucher_id = self.pool.get('account.voucher').search(self.cr, self.uid, [('move_id','in',ids)])
			if voucher_id:
				voucher = self.pool.get('account.voucher').browse(self.cr, self.uid, voucher_id)
				self.model = 'account.voucher'
				return voucher
			else:
				self.model = 'otro'
				return objects

	def fecha_documento(self, ref):
		invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('reference','=', ref)])
		voucher_ids = self.pool.get('account.voucher').search(self.cr, self.uid, [('reference','=', ref)])

		if len(invoice_ids) > 0:
			fecha = self.dates(3, self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids[0]).date_invoice)
		elif len(voucher_ids) > 0:
			fecha = self.dates(3, self.pool.get('account.voucher').browse(self.cr, self.uid, voucher_ids[0]).date)
		else:
			fecha = ' '
		return fecha

	def periodo(self, periodo):
		mes = periodo.split('/')[0]
		if mes == '01':
			return 'Enero'
		elif mes == '02':
			return 'Febrero'
		elif mes == '03':
			return 'Marzo'
		elif mes == '04':
			return 'Abril'
		elif mes == '05':
			return 'Mayo'
		elif mes == '06':
			return 'Junio'
		elif mes == '07':
			return 'Julio'
		elif mes == '08':
			return 'Agosto'
		elif mes == '09':
			return 'Septiembre'
		elif mes == '10':
			return 'Agosto'
		elif mes == '11':
			return 'Noviembre'
		elif mes == '12':
			return 'Diciembre'
		else:
			return periodo

	def descripcion(self, ref):
		invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('reference','=', ref)])
		voucher_ids = self.pool.get('account.voucher').search(self.cr, self.uid, [('reference','=', ref)])

		if len(invoice_ids) > 0:
			desc = self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids[0]).number
		elif len(voucher_ids) > 0:
			desc = self.pool.get('account.voucher').browse(self.cr, self.uid, voucher_ids[0]).name
		else:
			desc = ' '

		return desc

	def formatRut(self, rut):
		if rut:
			return rut[2:-7]+'.'+rut[-7:-4]+'.'+rut[-4:-1]+'-'+rut[-1:]
		return ''

	def suma(self, lineas, opc):
		total = 0
		if opc == '0':
			for obj in lineas:
				total += obj.debit
		elif opc == '1':
			for obj in lineas:
				total += obj.credit

		return total

	def get_create_date(self, obj_id, obj):
		self.cr.execute('SELECT create_date from '+str(obj)+' where id = '+str(obj_id))
		date = self.cr.dictfetchall()[0]['create_date'][:10]
		create_date = self.formatLang(date, date=True)
		return create_date

	def get_create_uid(self, obj_id, obj):
		self.cr.execute('SELECT create_uid from '+str(obj)+' where id = '+str(obj_id))
		user = self.cr.dictfetchall()[0]['create_uid']
		name = self.pool.get('res.users').browse(self.cr, self.uid, user).name
		return name

	def dates(self, option, date=None):
		if date:
			if int(option) == 0:
				return date.split('-')[2]
			elif int(option) == 1:
				return date.split('-')[1]
			elif int(option) == 2:
				return date.split('-')[0]
			elif int(option) == 3:
				splits = date.split('-')
				formatDate = str(splits[2])+"/"+str(splits[1])+"/"+str(splits[0])
				return formatDate
			elif int(option) == 4:
				today = datetime.date.today().strftime("%d/%m/%Y")
				return today
		return None

	def informacion(self, line_obj, opc):
		if line_obj.reconcile_id:
			for line in line_obj.reconcile_id.line_id:
				if line.debit != 0 and line.invoice:
					if opc == '0':
						return str(line.invoice.out_invoice_cc)
					elif opc == '1':
						return str(line.invoice.number)
					elif opc == '2':
						return str(self.dates(3, line.invoice.date_due))
					else:
						return None
				elif line.debit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
							and line.period_id.code == '00/2014':
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return None
				elif line.credit != 0 and\
						('NOTAS DE CREDITO' in line.journal_id.name or 'NOTA DE CREDITO' in line.journal_id.name):
					if opc == '0':
						nota_id = self.pool.get('account.invoice').search(self.cr, self.uid,\
									[('number','=',line.name),('type','=','out_refund')], limit=1)
						if nota_id:
							nota_obj = self.pool.get('account.invoice').browse(self.cr, self.uid, nota_id[0])
							return str(nota_obj.out_invoice_cc)
						else:
							return None
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return None
				elif line.credit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
						and line.period_id.code == '00/2014' and 'NOTA CREDITO' in line.name:
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return None
		elif line_obj.reconcile_partial_id:
			for line in line_obj.reconcile_partial_id.line_partial_ids:
				if line.debit != 0 and line.invoice:
					if opc == '0':
						return str(line.invoice.out_invoice_cc)
					elif opc == '1':
						return str(line.invoice.number)
					elif opc == '2':
						return str(self.dates(3, line.invoice.date_due))
					else:
						return None
				elif line.debit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
							and line.period_id.code == '00/2014':
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return None
				elif line.credit != 0 and\
						('NOTAS DE CREDITO' in line.journal_id.name or 'NOTA DE CREDITO' in line.journal_id.name):
					if opc == '0':
						nota_id = self.pool.get('account.invoice').search(self.cr, self.uid,\
									[('number','=',line.name),('type','=','out_refund')], limit=1)
						if nota_id:
							nota_obj = self.pool.get('account.invoice').browse(self.cr, self.uid, nota_id[0])
							return str(nota_obj.out_invoice_cc)
						else:
							return None
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return None
				elif line.credit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
						and line.period_id.code == '00/2014' and 'NOTA CREDITO' in line.name:
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return None
		else:
			return None
	
	def get_model(self):
		return self.model

report_sxw.report_sxw('report.l10n_cl_gestion_corbranza_report', 'account.move.line',\
		'l10n_cl_gestion_cobranza/report/template_account_voucher.rml', parser=Parser, header=False)

