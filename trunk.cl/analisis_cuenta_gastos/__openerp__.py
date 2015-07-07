{
	'name' : 'Analisis de Cuenta de Gastos',
	'version' : '1.0',
	'description': '''Genera un Reporte de Cuentas de Gastos por Periodo Actual en Comparación al Período del Ejercicio Fiscal Anterior,<br> Agrupado por Cuenta Analitica''',
	'author' : '[Development & System Engineering Departament OpenDrive Ltda.;]',
	'category' : 'Account Bank',
	'website' : '[http://www.opendrive.cl]',
	'depends' : ['base','account'],
	'data' : [
		'report/analisis_cuenta_gastos.xml',
		'wizard/analisis_cuenta_gastos.xml',
	],
	'installable': True,
	'active': False
}
