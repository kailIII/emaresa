from openerp.osv import osv, fields

class purchase_journal(osv.Model):
    _name = 'purchase.journal'
    _columns = {
            'name': fields.char('Name', size=32),
        }
    
class purchase_order(osv.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"
    _columns = {
            'purchase_journal_id': fields.many2one('purchase.journal', string="Purchase Journal", required=True,
                                                   states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
            'bitacora_bizagi': fields.text('Bitacora Bizagi', readonly=True),
        }
    