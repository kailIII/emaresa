import datetime
from report import report_sxw

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.cr = cr
		self.uid = uid
		
		self.localcontext.update({
			'lineas': self.lineas,
			'fecha_documento': self.fecha_documento,
			'ingreso': self.ingreso,
			'fecha_vencimiento': self.fecha_vencimiento,
			'tipo_doc': self.tipo_doc,
			'get_user': self.get_user,
			'get_create_date': self.get_create_date,
			'get_create_uid': self.get_create_uid,
			'descripcion': self.descripcion,
			'dates': self.dates,
			'monto': self.monto,
			'transferencia': self.transferencia,
			'periodo': self.periodo,
			'suma': self.suma,
			'formatRut': self.formatRut,
			# Cobranza
			'centro_costo': self.centro_costo,
			# Solicitud de Cargo
			'montos': self.montos,
			'cuenta': self.cuenta,
			'vencimiento': self.vencimiento,
			'division': self.division
		})

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

	def formatRut(self, rut):
		if rut:
			return rut[2:-7]+'.'+rut[-7:-4]+'.'+rut[-4:-1]+'-'+rut[-1:]
		return ''

	def centro_costo(self, line_obj, opc):
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
						return ' '
				elif line.debit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
							and line.period_id.code == '00/2014':
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return ' '
				elif line.credit != 0 and\
						('NOTAS DE CREDITO' in line.journal_id.name or 'NOTA DE CREDITO' in line.journal_id.name):
					if opc == '0':
						nota_id = self.pool.get('account.invoice').search(self.cr, self.uid,\
									[('number','=',line.name),('type','=','out_refund')], limit=1)
						if nota_id:
							nota_obj = self.pool.get('account.invoice').browse(self.cr, self.uid, nota_id[0])
							return str(nota_obj.out_invoice_cc)
						else:
							return ' '
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return ' '
				elif line.credit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
						and line.period_id.code == '00/2014' and 'NOTA CREDITO' in line.name:
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return ' '
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
						return ' '
				elif line.debit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
							and line.period_id.code == '00/2014':
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return ' '
				elif line.credit != 0 and\
						('NOTAS DE CREDITO' in line.journal_id.name or 'NOTA DE CREDITO' in line.journal_id.name):
					if opc == '0':
						nota_id = self.pool.get('account.invoice').search(self.cr, self.uid,\
									[('number','=',line.name),('type','=','out_refund')], limit=1)
						if nota_id:
							nota_obj = self.pool.get('account.invoice').browse(self.cr, self.uid, nota_id[0])
							return str(nota_obj.out_invoice_cc)
						else:
							return ' '
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return ' '
				elif line.credit != 0 and line.period_id.special and line.period_id.fiscalyear_id.name == '2014'\
						and line.period_id.code == '00/2014' and 'NOTA CREDITO' in line.name:
					if opc == '0' and line.centro_costo:
						return str(line.centro_costo)
					elif opc == '1':
						return str(line.name)
					elif opc == '2':
						return str(self.dates(3, line.date_maturity))
					else:
						return ' '
		else:
			return ' '
	
	def factura(self, name, descripcion, numero):
		if name in descripcion:
			return numero
		elif descripcion in name:
			return numero
		else:
			return name
		
	def lineas(self, lines_obj, cond):
		if cond == 0:
			objs1 = []
			for line in lines_obj:
				if not self.pool.get('account.analytic.line').search(self.cr, self.uid, [('move_id','=', line.id)]):
					objs1.append(line)
			return objs1
		elif cond == 1:
			objs2 = []
			for line in lines_obj:
				analytic_ids = self.pool.get('account.analytic.line').search(self.cr, self.uid, [('move_id','=', line.id)])
				if analytic_ids:
					for line_obj in self.pool.get('account.analytic.line').browse(self.cr, self.uid, analytic_ids):
						objs2.append(line_obj)
			return objs2
		return []

	def monto(self, monto, cond):
		if float(monto) < 0 and cond == 0:
			return int(monto)*-1
		elif float(monto) > 0 and cond == 1:
			return float(monto)
		else:
			return float(0)

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

	def ingreso(self, objeto):
		lista1 = []
		for obj in objeto:
			if obj.amount>0:
				lista1.append(obj)
		return lista1

	def fecha_vencimiento(self, ref, fecha_linea):
		invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('reference','=', ref)])
		voucher_ids = self.pool.get('account.voucher').search(self.cr, self.uid, [('reference','=', ref)])

		if len(invoice_ids) > 0:
			fecha = self.dates(3, self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids[0]).date_due)
		elif len(voucher_ids) > 0:
			fecha = self.dates(3, self.pool.get('account.voucher').browse(self.cr, self.uid, voucher_ids[0]).date_due)
		elif fecha_linea:
			fecha = self.dates(3, fecha_linea)
		else:
			fecha = ' '

		return fecha

	def tipo_doc(self, cond, ref):
		invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('reference','=', ref)])
		voucher_ids = self.pool.get('account.voucher').search(self.cr, self.uid, [('reference','=', ref)])

		if len(invoice_ids) > 0 and cond == 1:
			return ref
		elif len(voucher_ids) > 0 and cond == 2:
			return ref
		else:
			return 'S/N'

	def get_user(self):
		usuario = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).name
		return usuario

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

	def transferencia(self, ref, code):
		if code == '405':
			return ref
		else:
			return ' '

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

	def montos(self, lineas):
		for obj in lineas:
			if obj.account_id.code == '111519':
				return obj.debit or obj.credit
		return 0

	def cuenta(self, lineas):
		for obj in lineas:
			if obj.account_id.code == '111519':
				return obj.account_id.name
		return ''

	def vencimiento(self, lineas):
		for obj in lineas:
			if obj.account_id.code == '111519':
				return obj.date_maturity
		return ''

	def division(self, lineas):
		for obj in lineas:
			if obj.account_id.code == '111519':
				user_ids = self.pool.get('res.users').search(self.cr, self.uid, [('partner_id','=', obj.partner_id.id)])
				user_obj = self.pool.get('res.users').browse(self.cr, self.uid, user_ids[0])
				return user_obj.codecc
		return ''
	
	def suma(self, objetos):
		total = 0
		for num in objetos:
			total += num
		return total

report_sxw.report_sxw('report.account_voucher_report', 'account.voucher',\
		'account_report/report/template_account_voucher.rml', parser=Parser, header=False)
report_sxw.report_sxw('report.account_move_report', 'account.move',\
		'account_report/report/template_account_move.rml', parser=Parser, header=False)
report_sxw.report_sxw('report.account_move_cargo_report', 'account.move',\
		'account_report/report/template_account_move_cargo.rml', parser=Parser, header=False)

