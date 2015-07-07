# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv

class res_currency(osv.osv):
    _inherit = "res.currency"
    
    def _get_conversion_rate(self, cr, uid, from_currency, to_currency, context=None):
        res = super(res_currency, self)._get_conversion_rate(cr, uid, from_currency, to_currency, context=context)
        if context is None:
            context = {}
        if context.get('currency_rate_used', False):
            print "account_move_line_currency_rate - Warning: while running '_get_conversion_rate', context contains 'currency_rate_used' yet"
        context['currency_rate_used'] = res
        return res

res_currency()
