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

from osv import osv, fields

class hr_payslip_run_confirm_all(osv.osv):
	_inherit =  'hr.payslip.run'

	def confirm_all(self, cr, uid, ids, context=None):
		payslip = self.pool.get('hr.payslip')
		payslips_objs = payslip.browse(cr, uid,\
			payslip.search(cr, uid, [('payslip_run_id','in',ids)], context=context), context=context)

		for payslip in payslips_objs:
			resp1 = payslip.hr_verify_sheet()
			if resp1:
				resp2 = payslip.process_sheet()
		return True
hr_payslip_run_confirm_all()

