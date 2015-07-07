# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class account_move_line(osv.osv):

    _inherit = 'account.move.line'
    
    _columns = {
        'currency_rate_used': fields.float('Rate Used', digits=(12,6)),
        }
    
    def create(self, cr, uid, vals, context=None, check=True):
        if context is None:
            context = {}
        if vals.get('amount_currency', False) and not context.get('currency_rate_used', False):
            print "account_move_line_currency_rate - Warning: writing 'amount_currency' but context does not contain 'currency_rate_used'"
        elif vals.get('amount_currency', False) and context.get('currency_rate_used', False):
            vals.update({'currency_rate_used': context['currency_rate_used']})
        res = super(account_move_line, self).create(cr, uid, vals, context=context, check=check)
        #context['currency_rate_used'] = False
        return res
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if context is None:
            context = {}
        if vals.get('amount_currency', False) and not context.get('currency_rate_used', False):
            print "account_move_line_currency_rate - Warning: writing 'amount_currency' but context does not contain 'currency_rate_used'"
        elif vals.get('amount_currency', False) and context.get('currency_rate_used', False):
            vals.update({'currency_rate_used': context['currency_rate_used']})
        res = super(account_move_line, self).write(
            cr, uid, ids, vals, context=context, check=check, update_check=update_check)
        #context['currency_rate_used'] = False
        return res

account_move_line()
