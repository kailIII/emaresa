import datetime
from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.cr = cr
		self.uid = uid
		
		self.localcontext.update({
			'create_date': self.create_date,
			'create_uid': self.create_uid,
			'formatRut': self.formatRut,
			'suma': self.suma,
			'periodo': self.periodo
		})

	def suma(self, objetos):
		total = 0
		for num in objetos:
			total += num
		return total

	def create_date(self, obj_id):
		self.cr.execute('SELECT create_date from account_move_reconcile where id = '+str(obj_id))
		date = self.cr.dictfetchall()[0]['create_date'][:10]
		create_date = self.formatLang(date, date=True)
		return create_date

	def create_uid(self, obj_id):
		self.cr.execute('SELECT create_uid from account_move_reconcile where id = '+str(obj_id))
		user = self.cr.dictfetchall()[0]['create_uid']
		name = self.pool.get('res.users').browse(self.cr, self.uid, user).name
		return name

	def formatRut(self, rut):
		if rut:
			return rut[2:-7]+'.'+rut[-7:-4]+'.'+rut[-4:-1]+'-'+rut[-1:]
		return ''

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

report_sxw.report_sxw('report.account_move_reconcile_rml_report', 'account.move.reconcile',\
		'addons/emaresa/account_reconcile_modifier/report/template_account_move_reconcile.rml', parser=Parser, header=False)

