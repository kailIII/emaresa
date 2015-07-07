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
    'name' : 'Generador de libros electronicos para DBNet',
    'version' : '1.9',
    'category': 'Purchase Management',
    'depends' : ['base','purchase','sale'],
    'author' : 'David Acevedo (Fedoro), OpenDrive Ltda.',
    'description':
"""
V1.8 -> Modificado Nombre de libro quitando plural, nombres de clientes truncados a 50 caracteres maximo,\n
Rut formateado, verificados los campos de acuerdo al ejemplo enviado.\n
V1.9 -> Modificadas columnas correspondientes para formato de libro compra y agregada una columna con valor 0 antes del monto de las facturas\n
excentas.
""",
    'website': 'http://www.opendrive.cl',
    'data': [
	'reportes_electronicos_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
