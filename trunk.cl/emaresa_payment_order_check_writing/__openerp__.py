{
	'name' : 'Payment Order',
	'version' : '0.2',
	'description': """
Emaresa Payment Order Check Writing Module

Created By Alonso Molina,
Modified By David Acevedo.
""",
	'author' : '[OpenDrive Ltda]',
	'category' : 'Emaresa Check Print',
	'website' : '[http://www.opendrive.cl]',
	'depends' : ['base','account'],
	'init_xml' : [],
	'update_xml' : [
		'report/emaresa_payment_order_check_writing.xml',
	],
	'demo_xml' : [],
	'installable': True,
	'active': False
}
