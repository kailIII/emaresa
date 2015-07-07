# -*- coding: utf-8 -*-
##############################################################################
#
# Author: OpenDrive Ltda
# Copyright (c) 2013 Opendrive Ltda
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
        'name': 'Emaresa Protest Check',
        'version': '0.6.1',
        'author': '[OpenDrive Ltda]',
        'website': '[http://www.opendrive.cl]',
        'category': 'Localization',
        'description':
"""
Historial de Cambios:\n
v0.3 -> Agregado a dominio codigos de letras y pagares protestados\n
v0.4 -> Agregada metodo para bloqueo de clientes al pasar por los diarios:\n
'466','651','680','920','921','922','925','926','927','930','931','932','933','934','935' cada vez que se crea un asiento.\n
v0.5 -> Corregido error con web service al no poder encontrarlo o conectarse a el.\n
v0.6 -> Se agrega el campo funcion 'check number' para almacenar en el movimiento el campo 'name' del apunte contable, que en
el protesto es el numero de cheque y se elimina el campo 'invoice' de la vista de apuntes contables dentro del asiento.\n
v0.6.1 -> Se corrige el bloqueo de clientes que pasan por legalia, magallanes o cheques portestados.\n

Creado Por Alonso Molina, Modificado por David Acevedo Toledo (Fedoro).
""",
        'depends': ['base','account'],
        'data' : [
		'security/ir.model.access.csv',
		'l10n_cl_emaresa_protest_check_view.xml',
		'check_customize_view.xml'
	],

	'installable': True,
	'application': True,
	'auto_install': False,
	'active': False
}
