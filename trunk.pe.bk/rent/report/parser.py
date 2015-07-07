from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		self.item = 0

		self.localcontext.update({
			'get_item': self.get_item,
		})

	def get_item(self):
		self.item += 1
		return self.item

