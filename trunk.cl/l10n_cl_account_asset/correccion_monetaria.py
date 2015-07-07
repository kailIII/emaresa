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

class correccion_monetaria(osv.osv):
	_name = 'correccion.monetaria'
#	_description = 'Tabla que guarda los valores para ejecutar correccion monetaria mensual de cada activo'

	_columns = {
		'name':fields.char('Nombre', size=64, required=True, readonly=False),
		'periodo':fields.many2one('account.period','Periodo', required=True, readonly=False),
		'company_id':fields.many2one('res.company','Company', requider=True, readonly=False),
		'valor_cm_af':fields.float('Valor CM Act. Fijo', required=True, readonly=False),
		'valor_cm_dep':fields.float('Valor CM Depreciacion', required=True, readonly=False),
		'asset_asset_id':fields.many2one('account.asset.asset','Id Activo', required=True, readonly=False),
		'asset_dep_id':fields.many2one('account.asset.depreciation.line','Id Depreciacion', required=True, readonly=False)
	}
correccion_monetaria()

