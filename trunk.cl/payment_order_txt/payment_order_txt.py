##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
import base64, cStringIO
	

class pago_txt(osv.osv):
	_inherit = 'payment.order'

	_columns = {
		'file_name':fields.char('Nombre', size=25, readonly=True),
		'file':fields.binary('reporte txt', readonly=True),
	}

	_default = {
		'file_name': 'nomina_pago.txt',
	}

	def archivo_bci(self,cr,uid,ids,context={}):       
		data =''
		data2 = cStringIO.StringIO()

  		for payment_line in self.pool.get('payment.order').browse(cr,uid,ids)[0].line_ids:
			if len(str(payment_line.partner_id.vat).replace('CL','')) < 9:
				Rut_Proveedor='0'+str(payment_line.partner_id.vat).replace('CL','')
			else:
				Rut_Proveedor=str(payment_line.partner_id.vat).replace('CL','')
			Razon_Social=(payment_line.partner_id.name if payment_line.partner_id.name else '').ljust(45)[0:44]
			rs = Razon_Social.encode('utf-8')
			Forma_de_Pago=' '+str(payment_line.bank_id.state if payment_line.bank_id else'').ljust(3)+''.ljust(1)[-1:3]
			Codigo_de_Banco_Destino=str(payment_line.bank_id.bank.bic if payment_line.bank_id else '').rjust(3).replace(' ','0')+''.ljust(1)[:-1]
			Cuenta_de_Abono=str(payment_line.bank_id.acc_number if payment_line.bank_id else '').replace(' ','').replace('-','0').rjust(20,'0')+''.ljust(1)[:-1]
			Identificador_Documento=str(payment_line.communication if payment_line.communication and payment_line.communication.isnumeric() else '').rjust(10).replace(' ','0')+''.ljust(1)[:-1]
			factura=str(payment_line.communication if payment_line.communication and payment_line.communication.isnumeric() else '')
			Monto_a_Pago=str(int(payment_line.amount) if payment_line.amount else '').rjust(12).replace(' ','0')+''.ljust(1)[:-1]
			Codigo_de_Oficina_de_Pago=''.rjust(3)+''.ljust(1)[:-1]
			#fecha=str(payment_line.date if payment_line.date else '').ljust(8).replace('-','')+''.ljust(1)
			dia=str(payment_line.date).split('-')[2]		
			mes=str(payment_line.date).split('-')[1]
			ano=str(payment_line.date).split('-')[0]
			Fecha_de_Pago=str(dia+mes+ano)
#			Fecha_de_Pago=str(payment_line.date if payment_line.date else '').ljust(8).replace('-','')+''.ljust(1)[:-1]+'holiholi'
			Apellido_Paterno_Retirador=''.ljust(15)+''.ljust(1)
			Apellido_Materno_Retirador=''.ljust(15)+''.ljust(1)
			Nombres_Retirador=''.ljust(15)+''.ljust(1)
			#Rut_Retirador=''.ljust(8)+''.ljust(1)
			#DV_Retirador=''.ljust(1)+''.ljust(1)
			espacios=' '*6
#			espacios2=' '*4
			Tipo_de_Documento='FAC'.ljust(3)+''.ljust(1)[:-1]
#			Glosa=str(payment_line.communication2 if payment_line.communication2 else '').ljust(35)+''.ljust(1)[:-1]			
			Glosa = str("NRO DOC "+factura)
			Medio_de_aviso='E'
			Direccion_de_aviso=str(payment_line.partner_id.email if payment_line.partner_id.email else '').ljust(30)[0:30]
			if Forma_de_Pago.strip()== 'VVC':
				data += Rut_Proveedor+rs+Forma_de_Pago+Codigo_de_Banco_Destino+Cuenta_de_Abono+Identificador_Documento+Monto_a_Pago+'245'+Fecha_de_Pago+Apellido_Paterno_Retirador+Apellido_Materno_Retirador+Nombres_Retirador+espacios+Tipo_de_Documento+Medio_de_aviso+Direccion_de_aviso+espacios[:-1]+Glosa+"\r\n"
			else:
				data += Rut_Proveedor+rs+Forma_de_Pago+Codigo_de_Banco_Destino+Cuenta_de_Abono+Identificador_Documento+Monto_a_Pago+Codigo_de_Oficina_de_Pago+Fecha_de_Pago+Apellido_Paterno_Retirador+Apellido_Materno_Retirador+Nombres_Retirador+espacios+Tipo_de_Documento+Medio_de_aviso+Direccion_de_aviso+espacios[:-1]+Glosa+"\r\n"

		data2.write(data)
		out = base64.encodestring(data2.getvalue())
		data2.close()
		self.write(cr, uid, ids, {'file': out, 'file_name': 'nomina_pago.txt'}, context=context)

		return True


