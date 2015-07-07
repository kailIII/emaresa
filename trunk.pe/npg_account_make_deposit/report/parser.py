from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)

		self.localcontext.update({ })

report_sxw.report_sxw('report.account_deposit_ticket_rml_report', 'deposit.ticket',\
			'npg_account_make_deposit/report/template_deposit_receipt.rml', parser=Parser, header=False)
