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

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'spot_bank_journal_id': fields.many2one(
            'account.journal',
            string="SPOT Bank Journal",
            domain="[('type', '=', 'bank')]",
            help="SPOT bank journal, for example the default bank/cash account used  to pay supplier detractions",),
        'detraction_journal_id': fields.many2one(
            'account.journal',
            string="Detractions Bank Journal",
            domain="[('type', '=', 'bank')]",
            help="Detraction bank account journal, this is the bank account detraction owned by the company",),
    }

res_company()