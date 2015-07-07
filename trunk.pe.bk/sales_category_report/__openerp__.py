{
	'name' : 'sales_category_report',
	'version' : '0.1',
	'description': '''Permite un nivel de analisis por estructura de categorias de productos en Reporte Analisis de ventas.''',
	'author' : '[OpenDrive Ltda]',
	'category' : 'report',
	'website' : '[http://www.opendrive.cl]',
	'depends' : ['sale', 'stock', 'procurement'],
	'init_xml' : [],
	'update_xml' : [
		'sale_report_view.xml',
	],
	'demo_xml' : [],
	'installable': True,
	'active': False
}
