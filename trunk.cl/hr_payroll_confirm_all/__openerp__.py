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
    'name' : 'hr_payroll_confirm_all',
    'version' : '0.1',
    'author' : '[Stratanet Ltda | David Acevedo Toledo; OpenDrive Ltda]',
    'category' : 'Human Resources',
    'description' : """
    	Modulo que agrega boton "confirmar todos" a vista de nominas de pago de empleados
    """,
    'website': '[http://www.stratanet.cl; http://www.opendrive.cl]',
    'depends' : ['hr_payroll'],
    'data': [
#    	'security/ir.model.access.csv',
	'hr_payroll_payall_view.xml',
 #   	'account_asset_category_view.xml',
#	'wizard/account_asset_correccion_monetaria_view.xml',
	#'report/account_payment_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
