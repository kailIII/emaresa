# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from tools.translate import _

class account_asset_asset(osv.osv):
    _name = 'account.asset.asset'
    _inherit = 'account.asset.asset'        
    
    def _amount_residual_re(self, cr, uid, ids, name, args, context=None):        
        cr.execute("""SELECT
                l.asset_id as id, SUM(abs(l.amount)) AS amount
            FROM
                account_asset_depreciation_line l
            WHERE
                l.asset_id IN %s AND l.move_check = True GROUP BY l.asset_id """, (tuple(ids),))                
        res=dict(cr.fetchall())
        for asset in self.browse(cr, uid, ids, context):
            print asset.purchase_value
            print res.get(asset.id, 0.0)
            print asset.salvage_value                
            res[asset.id] = asset.purchase_value - res.get(asset.id, 0.0) - asset.salvage_value        
        for id in ids:
            res.setdefault(id, 0.0)
        return res
    
    _columns = {
                'value_residual_re': fields.function(_amount_residual_re, method=True, store=True,digits_compute=dp.get_precision('Account'), string='Activo Fijo Neto'),
                }
    
        
account_asset_asset()    
