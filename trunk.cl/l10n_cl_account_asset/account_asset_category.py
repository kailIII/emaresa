# -*- encoding: utf-8 -*-
#
# Author: OpenDrive Ltda
# Copyright (c) 2013 Opendrive Ltda
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from osv import osv, fields

class asset_category_type(osv.osv):
	_inherit = 'account.asset.category'

	_columns = {
		'accounting_type':fields.selection([('tributario','Tributario'),('ifrs','IFRS')], 'Tipo Contable', required=True, readonly=False),
		'account_correccion_monetaria_id':fields.many2one('account.account', 'Account Correccion Monetaria'),
	}
asset_category_type()
