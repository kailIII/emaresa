{
'name':'actualizacion automatica monedas Econube',
"version": "1.0",
'description':'''
Actualizacion automatica paridad de tipos de cambio Econube
==================

Este modulo agrega dos campos a el modelo res_currency; un boolean para indicar si la moneda debe ser actualizada y un char para indicar el codigo de la moneda en el Banco Central de Chile
''',
'category':'currency',
'author':'Nelson Diaz Navarro',
'depends':['base','account',],
'data':['res_currency_select_automatic_update.xml',],
'active':True,
'installable':True,
}