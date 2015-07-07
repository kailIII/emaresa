from openerp.osv import osv, fields
import time
from datetime import timedelta,date,datetime
from openerp.tools.translate import _ 

class info_check_voucher(osv.osv):
   _inherit = 'account.voucher'
   _description = 'banco origen'
   _columns = {
        'origin_bank': fields.many2one('res.bank','Banco Origen'),
    }

info_check_voucher()
