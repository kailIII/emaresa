# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    _columns = {
        'spot_bank_journal_id': fields.related(
            'company_id', 'spot_bank_journal_id',
            type='many2one',
            relation='account.journal',
            string="SPOT Bank Journal"),
        'detraction_journal_id': fields.related(
            'company_id', 'detraction_journal_id',
            type='many2one',
            relation='account.journal',
            string="Detraction Bank Journal"),
    }
