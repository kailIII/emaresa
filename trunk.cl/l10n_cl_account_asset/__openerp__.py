# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: OpenDrive Ltda
#    Copyright (c) 2013 Opendrive Ltda
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'l10n CL Account Asset',
    'version' : '1.9',
    'author' : '[OpenDrive Ltda]',
    'category' : 'Accounting & Finance',
    'description' :
"""
	Modulo corrección monetaria de activos fijos y depreciacion por categorias agrupadas para Chile 2013.

	Change Log
	V1.6	-> Integracion de funcion que calcula la depreciacion agrupando los valores en el asiento por categoria.\n
		-> Se elimina menu para confirmar lineas de la carga inicial para evitar confuciones.\n
		-> Se reordenan los menu para correccion monetaria y depreciacion.\n
	V1.7	-> Se corrigen las cuentas de las lineas del asiento para la depreciacion en el boton para acumular por categoria y se corrige el journal.\n
	V1.8	-> Se Agrega la creacion de lineas analiticas por cada centro de costo agrupado.\n
	V1.9	-> Se agrega la cuenta de correccion monetaria en la categoria de activo para el asiento de baja.\n
""",
    'website': '[http://www.opendrive.cl]',
    'depends' : ['account_asset', 'stock'],
    'data': [
	'security/ir.model.access.csv',
	'account_asset_view.xml',
	'account_asset_confirm_view.xml',
	'account_asset_category_view.xml',
	'account_asset_invoice_view.xml',
	'stock_view.xml',
	'wizard/account_asset_correccion_monetaria_view.xml',
	'wizard/account_asset_depreciacion_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
