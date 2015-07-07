from openerp.osv import osv, fields
import time
from datetime import timedelta,date,datetime
from openerp.tools.translate import _ 

class user_account_move_line(osv.osv):
   _inherit = 'account.move.line'
   _description = 'Agrega usuario en apunte'
   _columns = {
        'user_id': fields.many2one('res.users','Usuario', readonly=True, states={'draft':[('readonly',False)]}),
        'centro_costo': fields.char('centro_costo', size=64),
        'ref2': fields.char('ref2', size=64),
    }

user_account_move_line()