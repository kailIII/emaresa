from openerp.osv import osv, fields
import time
from datetime import timedelta,date,datetime
from openerp.tools.translate import _ 

class account_journal_iddocumentoemaresa(osv.osv):
   _inherit = 'account.journal'
   _description = 'Agrega tipo de documento de emaresa a diarios de OpenERP'
   _columns = {
        'tipo_doc_emaresa': fields.char('Tipo Documento Emaresa', size=64),
    }

account_journal_iddocumentoemaresa()