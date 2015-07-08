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
	'name' : 'Lock/Unlock Partners',
	'version' : '1.2.5_1',
	'author' : '[OpenDrive Ltda]',
	'category' : 'Others/Partners',
	'description' : """
Modulo bloqueo de clientes para ventas.
Crones, Fecha Hasta, Tramos de valores para centros de costos, Cheques vencidos y pagos al dia no realizados.

Created By David Acevedo Toledo (Fedoro)
""",
	'website': '[http://www.opendrive.cl]',
	'depends' : ['base', 'warning', 'l10n_cl_fields'],
	'data': [
		'security/ir.model.access.csv',
		'wizard/lock_unlock_process_view.xml',
		'cron_data.xml',
		'tramos_view.xml',
		'res_partner_view.xml'
	],
	'installable': True,
	'auto_install': False,
}
