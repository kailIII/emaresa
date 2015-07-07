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
from openerp.tools.translate import _

class account_followup_report(osv.osv):
	_inherit = 'res.partner'

	def do_aeroo_print(self, cr, uid, wizard_partner_ids, data, context=None):
		#wizard_partner_ids are ids from special view, not from res.partner
		if not wizard_partner_ids:
			return {}

		data['partner_ids'] = wizard_partner_ids

		datas = {
			'ids': [],
			'model': 'account_followup.followup',
			'form': data
		}

		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'followup_cta_cte_report',
			'datas': datas,
		}

	def print_report(self, cr, uid, ids, context=None):
		assert(len(ids) == 1)
		company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
		#search if the partner has accounting entries to print. If not, it may not be present in the
		#psql view the report is based on, so we need to stop the user here.
		if not self.pool.get('account.move.line').search(cr, uid, [
								('partner_id', '=', ids[0]),
								('account_id.type', '=', 'receivable'),
								('reconcile_id', '=', False),
								('state', '!=', 'draft'),
								('company_id', '=', company_id),
							], context=context):
			raise osv.except_osv(_('Error!'),\
				_("The partner does not have any accounting entries to print in the overdue report for the current company."))
		self.message_post(cr, uid, [ids[0]], body=_('Printed overdue payments report'), context=context)
		#build the id of this partner in the psql view. Could be replaced by a search with
	        #[('company_id', '=', company_id),('partner_id', '=', ids[0])]
		wizard_partner_ids = [ids[0] * 10000 + company_id]
		followup_ids = self.pool.get('account_followup.followup').search(cr, uid, [('company_id', '=', company_id)], context=context)
		if not followup_ids:
			raise osv.except_osv(_('Error!'),_("There is no followup plan defined for the current company."))
		data = {
			'date': fields.date.today(),
			'followup_id': followup_ids[0],
		}
		#call the print overdue report on this partner
		return self.do_aeroo_print(cr, uid, wizard_partner_ids, data, context=context)


	def do_aeroo_print_without_header(self, cr, uid, wizard_partner_ids, data, context=None):
		#wizard_partner_ids are ids from special view, not from res.partner
		if not wizard_partner_ids:
			return {}

		data['partner_ids'] = wizard_partner_ids

		datas = {
			'ids': [],
			'model': 'account_followup.followup',
			'form': data
		}

		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'followup_cta_cte_without_header_report',
			'datas': datas,
		}

	def print_report_without_header(self, cr, uid, ids, context=None):
		assert(len(ids) == 1)
		company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
		#search if the partner has accounting entries to print. If not, it may not be present in the
		#psql view the report is based on, so we need to stop the user here.
		if not self.pool.get('account.move.line').search(cr, uid, [
								('partner_id', '=', ids[0]),
								('account_id.type', '=', 'receivable'),
								('reconcile_id', '=', False),
								('state', '!=', 'draft'),
								('company_id', '=', company_id),
							], context=context):
			raise osv.except_osv(_('Error!'),\
				_("The partner does not have any accounting entries to print in the overdue report for the current company."))
		self.message_post(cr, uid, [ids[0]], body=_('Printed overdue payments report'), context=context)
		#build the id of this partner in the psql view. Could be replaced by a search with
		#[('company_id', '=', company_id),('partner_id', '=', ids[0])]
		wizard_partner_ids = [ids[0] * 10000 + company_id]
		followup_ids = self.pool.get('account_followup.followup').search(cr, uid, [('company_id', '=', company_id)], context=context)
		if not followup_ids:
			raise osv.except_osv(_('Error!'),_("There is no followup plan defined for the current company."))
		data = {
			'date': fields.date.today(),
			'followup_id': followup_ids[0],
		}
		#call the print overdue report on this partner
		return self.do_aeroo_print_without_header(cr, uid, wizard_partner_ids, data, context=context)
account_followup_report()

