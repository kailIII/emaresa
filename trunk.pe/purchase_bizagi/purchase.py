from openerp.osv import osv, fields
from openerp import netsvc
from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement


class purchase_journal(osv.Model):
    _name = 'purchase.journal'
    _columns = {
            'name': fields.char('Name', size=32),
        }

class purchase_log_bizagi(osv.Model):
    _name = 'purchase.log.bizagi'
    _columns = {
            'order_id': fields.many2one('purchase.order', string='Purchase Order', ondelete='cascade'),
            'bizagi_user': fields.char('Bizagi User', size=64),
            'bizagi_state': fields.char('Bizagi State', size=32),
            'bizagi_date': fields.datetime('Bizagi Date', size=32),
            'bizagi_approve_level': fields.char('Bizagi Approve Level', size=64),
            'bizagi_details': fields.text('Bizagi Details'),
        }

    
class purchase_order(osv.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"
    _columns = {
            'purchase_journal_id': fields.many2one('purchase.journal', string="Purchase Journal", required=True,
                                                   states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
            'bitacora_bizagi': fields.text('Bitacora Bizagi', readonly=True),
            'bizagi_log': fields.one2many('purchase.log.bizagi', 'order_id', string="Bizagi Log", readonly=True),
            'date_confirm':fields.date('Date Confirmed', readonly=1, select=True, help="Date on which purchase order has been confirmed"),
        }
    
    def action_approve_bizagi(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for order_id in ids:
            wf_service.trg_validate(uid, 'purchase.order', order_id, 'bizagi_approve', cr)
        return True
    
    def action_cancel_bizagi(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for order_id in ids:
            wf_service.trg_validate(uid, 'purchase.order', order_id, 'bizagi_cancel', cr)
        return True
    
    def action_send_bizagi(self, cr, uid, ids, context=None):
        client = SoapClient(wsdl="http://172.17.40.93/Procesos/webservices/WorkflowEngineSOA.asmx?wsdl")
        for order in self.browse(cr, uid, ids, context=context):
            detalle = ""
            for line in order.order_line:
                detalle += """
                                        <detalle>
                                            <producto>%s</producto>
                                            <descripcion>%s</descripcion>
                                            <precio>%s</precio>
                                         </detalle>                
                """%(line.product_id.default_code,
                     line.name,
                     line.price_unit)
            result = client.createCasesAsString("""
            <BizAgiWSParam xmlns="">
                    <domain>domain</domain>
                    <userName>admon</userName>
                    <Cases>
                        <Case>
                            <Process>PruebasRCV</Process>
                            <Entities>
                                <PruebasRCV>
                                    <nrosolicitud>%s</nrosolicitud>
                                    <solicitante>%s</solicitante>
                                    <tipo>%s</tipo>
                                    <detalle>
                                        %s
                                    </detalle>
                                    <open_order_id>%s</open_order_id>
                                </PruebasRCV>
                            </Entities>
                        </Case>
                    </Cases>
                </BizAgiWSParam>"""%(order.name, 
                                     order.validator.name, 
                                     order.purchase_journal_id.name,
                                     detalle,
                                     order.id))
            self.write(cr, uid, [order.id], {'bitacora_bizagi': result, 
                                             'date_confirm': fields.date.context_today('purchase.order', cr, uid, context=context)})

        