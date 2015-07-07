# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 OpenDrive Ltda. (<http://www.opendrive.cl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from osv import osv, fields

class account_analytic_line(osv.osv):
	_inherit = 'account.analytic.line'

	def _get_lines(self, cr, uid, ids, context=None):
		for move in self.browse(cr, uid, ids, context=context):
			for line in move.line_id:
				analytic_id = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id)], context=context)
				if analytic_id:
					return analytic_id
		return []


	_columns = {
		'period_id':fields.related('move_id', 'move_id', 'period_id', string='Period', type='many2one', relation='account.period',
			select=True, store={
				'account.move': (_get_lines, ['period_id'], 10),
				'account.analytic.line': (lambda *a: a[3], [], 20)
			})
	}
account_analytic_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
