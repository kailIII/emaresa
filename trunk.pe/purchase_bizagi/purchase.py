from openerp.osv import osv, fields
from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement


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
    
    def action_send_bizagi(self, cr, uid, ids, context=None):
        client = SoapClient(wsdl="http://172.17.40.93/Procesos/webservices/WorkflowEngineSOA.asmx?wsdl")
        for order in self.browse(cr, uid, ids, context=context):
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
                                        <detalle>
                                            <producto>7024000400213</producto>
                                            <descripcion>PAD CAFE 13"</descripcion>
                                            <precio>1525</precio>
                                         </detalle>
                                         <detalle>
                                            <producto>7024000400214</producto>
                                            <descripcion>CADENA 33 MM</descripcion>
                                            <precio>88542</precio>
                                         </detalle>
                                         <detalle>
                                            <producto>7024000400215</producto>
                                            <descripcion>DESECHOS TOXICOS</descripcion>
                                            <precio>5000</precio>
                                         </detalle>
                                    </detalle>
                                </PruebasRCV>
                            </Entities>
                        </Case>
                    </Cases>
                </BizAgiWSParam>"""%(order.name, order.validator.name, order.purchase_journal_id.name))
            self.write(cr, uid, [order.id], {'bitacora_bizagi': result})

        