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
	'name': 'Reportes Tributarios',
	'version': '0.6.3',
	'author': '[OpenDrive Ltda]',
	'website': 'http://opendrive.cl',
	'category': 'Localizacion Chilena',
	'description':
"""
Reportes Tributarios Balance Tributario, Libro de Compras, Libro de Ventas.

""",
	'depends': ['base', 'account', 'account_financial_report', 'report_aeroo_ooo'],
	'images': ['static/src/img/excel_icon.png', 'static/src/img/pdf_icon.png'],
	'data': [
		'wizard/reportes_view.xml',
		'report/reportes_reports.xml',
		'report/balance_trece.xml'
	],
	'installable': True,
}
