# -*- encoding: utf-8 -*-
#
# OpenERP Rent - A rent module for OpenERP 6
# Copyright (C) 2010-Today Thibaut DIRLIK <thibaut.dirlik@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging, datetime, time, re, netsvc

from osv import osv, fields
from tools.translate import _
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

from openlib.orm import *

_logger = logging.getLogger('rent')

class stock_move(osv.osv):
	_inherit = 'stock.move'
	_columns = {
		'rent_line_id':fields.many2one('rent.order.line', 'Rent Order Line', ondelete='set null', select=True),
	}

	_defaults = {
		'rent_line_id': False
	}
stock_move()

class stock_picking(osv.osv):
	_inherit = 'stock.picking'
	_columns = {
		'rent_id': fields.many2one('rent.order', 'Rent Order', ondelete='set null', select=True),
	}

	_defaults = {
		'rent_id': False
	}
stock_picking()


#class stock_partial_picking(osv.osv, ExtendedOsv):
#    _inherit = 'stock.partial.picking'

#    def do_partial(self, cr, uid, ids, context=None):
#        """Agrego funcion de llamado a cambio de fechas en action_process original"""
#	assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
#	stock_picking = self.pool.get('stock.picking')
#	stock_move = self.pool.get('stock.move')
#	uom_obj = self.pool.get('product.uom')
#	partial = self.browse(cr, uid, ids[0], context=context)
#	partial_data = {
#		'delivery_date' : partial.date
#	}

#	picking_type = partial.picking_id.type
#	for wizard_line in partial.move_ids:
#		line_uom = wizard_line.product_uom
#		move_id = wizard_line.move_id.id

		#Quantiny must be Positive
#		if wizard_line.quantity < 0:
#			raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

		#Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
#		qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

#		if line_uom.factor and line_uom.factor <> 0:
#			if qty_in_line_uom <> wizard_line.quantity:
#				raise osv.except_osv(_('Warning'), _('The uom rounding does not allow you to ship "%s %s", only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
#		if move_id:
			#Check rounding Quantity.ex.
			#picking: 1kg, uom kg rounding = 0.01 (rounding to 10g), 
			#partial delivery: 253g
			#=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
#			initial_uom = wizard_line.move_id.product_uom
			#Compute the quantity for respective wizard_line in the initial uom
#			qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
#			without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
#			if qty_in_initial_uom <> without_rounding_qty:
#				raise osv.except_osv(_('Warning'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
#		else:
#			seq_obj_name =  'stock.picking.' + picking_type
				
			#AKI MISMO SE HACE EL TEMA DE LA BODEGA DE LLEGADA
#			move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
#							'product_id': wizard_line.product_id.id,
#							'product_qty': wizard_line.quantity,
#							'product_uom': wizard_line.product_uom.id,
#							'prodlot_id': wizard_line.prodlot_id.id,
#							'location_id' : wizard_line.location_id.id,
#							'location_dest_id' : wizard_line.location_dest_id.id,
#							'picking_id': partial.picking_id.id
#							},context=context)
#			stock_move.action_confirm(cr, uid, [move_id], context)

#		partial_data['move%s' % (move_id)] = {
#			'product_id': wizard_line.product_id.id,
#			'product_qty': wizard_line.quantity,
#			'product_uom': wizard_line.product_uom.id,
#			'prodlot_id': wizard_line.prodlot_id.id,
#		}

#		if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
#			partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
#									product_currency=wizard_line.currency.id)
#	stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context)

	#########################################################################################################
	################################### Llamado a Funcion Salida ############################################
	#########################################################################################################
#	if (picking_type == 'out' and re.match("(RENT)\d\d\d\d\d\d\d",str(partial.picking_id.origin))):
#		self.generarEntradas(cr, uid, ids, partial, context)
	#########################################################################################################
	################################### Llamado a Funcion Entrada ###########################################
	#########################################################################################################
#	if (picking_type == 'in' and re.match("(RENT)\d\d\d\d\d\d\d",str(partial.picking_id.origin))):
#		self.cambiarFechasEntrada(cr, uid, ids, partial, context)

#	return {'type': 'ir.actions.act_window_close'}

#    def cambiarFechasEntrada(self, cr, uid, ids, partial, context=None):
#        """Cambia la fecha de devolución de cada linea de la orden de arriendo por la fecha actual"""

#	res = {}
#	move_line_ids = []

#	if not partial:
#		return False

#	reference = partial.picking_id.origin
#	order_id = self.pool.get('rent.order').search(cr, uid, [('reference','=',reference)], context=context)
#	order_obj = self.pool.get('rent.order').browse(cr, uid, order_id, context=context)[0]
#	line_ids = self.pool.get('rent.order.line').search(cr, uid, [('order_id','=',order_id)], context=context)
#	line_obj = self.pool.get('rent.order.line').browse(cr, uid, line_ids, context=context)

	# IDs de las lineas para modificar la fecha
#	for picking_line in partial.move_ids:
#		move_line_ids.append(picking_line.move_id.rent_line_id.id)
	
#	for line_id in line_ids:
#		res[line_id] = {
#			'date_begin': False,
#			'date_end': False,
#			'rent_duration_unity': False,
#		}

#	cr.execute('SELECT r.id, r.date_begin_rent, r.date_in_shipping, p.name FROM rent_order_line AS r\
#			INNER JOIN product_uom AS p ON (r.rent_duration_unity = p.id)\
#			INNER JOIN rent_order AS ro ON (r.order_id = ro.id)\
#			INNER JOIN stock_picking AS sp ON (ro.reference=sp.origin)\
#			WHERE ro.id=%s AND sp.type=%s;',(order_id[0],'in'))

#	for line_id, date_begin, date_end, tipo in cr.fetchall():
#		res[line_id]['date_begin'] = date_begin
#		res[line_id]['date_end'] = date_end
#		res[line_id]['rent_duration_unity'] = tipo

#	date_in = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

#	for line in line_obj:
#		if date_in < res[line.id]['date_end'] and line.id in move_line_ids:
#			duration = self.correct_date(res[line.id]['date_begin'], date_in, res[line.id]['rent_duration_unity'])
	
#			cr.execute('UPDATE rent_order_line set date_in_shipping=%s, invoicing_date=%s,\
#				 rent_duration=%s, date_end_rent=%s where id=%s',\
#					(date_in, date_in, duration, date_in, line.id))
#			cr.execute('UPDATE stock_picking set min_date=%s where id=%s',(date_in, partial.picking_id.id))
#			cr.execute('UPDATE stock_move set date_expected=%s where picking_id=%s',(date_in, partial.picking_id.id))
#	return True


#    def cambiarFechasSalida(self, cr, uid, ids, partial, context):
	
#	return True


#    def generarEntradas(self, cr, uid, ids, partial, context):
#	if not partial:
#		return False
	
#	cond = True
#	reference = partial.picking_id.origin
#	sequence_obj = self.pool.get('ir.sequence')
#	order_id = self.pool.get('rent.order').search(cr, uid, [('reference','=',reference)], context=context)
#	order_obj = self.pool.get('rent.order').browse(cr, uid, order_id, context)[0]
#	line_ids = []

	# Compruebo si la orden genera la salida por si misma al entregar todos los productos de una sola vez
#	if not order_obj.out_picking_id:
#		cond = False
#	else:
#		lines = self.pool.get('rent.order').get(order_id[0]).out_picking_id.move_lines or []
#		cond = all(line.state == 'done' for line in lines)
#
#	if cond:
#		for wizard in partial.move_ids:
#			line_ids.append(wizard.move_id.rent_line_id.id)
		#Cambio estado de las lineas
#		self.pool.get('rent.order.line').write(cr, uid, line_ids, {'state' : 'ongoing'})

#	else:
#		in_picking_id = self.pool.get('stock.picking').create(cr, uid, {
#			'name': sequence_obj.get(cr, uid, 'stock.picking.in'),
#			'origin': order_obj.out_picking_id.origin,
#			'type': 'in',
#			'state': 'auto',
#			'move_type': 'direct',
#			'rent_id': order_obj.id,
#			'invoice_state' : 'none',
#			'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#			'company_id': order_obj.company_id.id,
#			'partner_id': order_obj.partner_id.id
#		})

#		for wizard in partial.move_ids:
#			line_ids.append(wizard.move_id.rent_line_id.id)
#			move_id = self.pool.get('stock.move').create(cr, uid, {
#				'name': wizard.product_id.name,
#				'picking_id': in_picking_id,
#				'product_id': wizard.product_id.id,
#				'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#				'product_qty': wizard.quantity,
#				'product_uom': wizard.product_uom.id,
#				'location_id': wizard.location_id.id,
#				'location_dest_id' : wizard.location_dest_id.id,
#				'state': 'draft',
#				'rent_line_id': wizard.move_id.rent_line_id.id
#			})
#			self.pool.get('stock.move').action_confirm(cr, uid, [move_id], context)
	
#		self.write(cr, uid, order_obj.id, {'in_picking_id' : in_picking_id})
	
		# Confirm the picking
#		netsvc.LocalService("workflow").trg_validate(uid, 'stock.picking', in_picking_id, 'button_confirm', cr)
		# Check assignement (TODO: This should be optional)
#		self.pool.get('stock.picking').action_assign(cr, uid, [in_picking_id])
		
		#Cambio estado de las lineas de la orden de arriendo
#		self.pool.get('rent.order.line').write(cr, uid, line_ids, {'state' : 'ongoing'})

#	return True

#    def correct_date(self, rent_begin, rent_end, tipo):
    	
#	"""
#	This method is called when the duration or duration unity changed. Input shipping date
#	is updated to be set at the end of the duration automatically.
#	"""

#	if not rent_begin or not rent_end:
#		return {}

#	begin =  rent_begin
#	end_  =  rent_end

#	aux_p = str(begin)
#	aux_e = str(end_)

#	dia_b = aux_p[8]+aux_p[9]
#	mes_b = aux_p[5]+aux_p[6]
#	agno_b = aux_p[0]+aux_p[1]+aux_p[2]+aux_p[3]
	
#	dia_e = aux_e[8]+aux_e[9]
#	mes_e = aux_e[5]+aux_e[6]
#	agno_e = aux_e[0]+aux_e[1]+aux_e[2]+aux_e[3]
	
#	aux_begin =  dia_b + mes_b +agno_b
#	aux_end  =   dia_e + mes_e + agno_e
	
#	cast_begin = datetime.datetime.strptime(aux_begin, '%d%m%Y').date()
#	cast_end   = datetime.datetime.strptime(aux_end, '%d%m%Y').date()
#	cal_dias   = cast_end - cast_begin
#	ct_cl_di   = str(cal_dias)

#	if ct_cl_di[2]=='d':
#		di_as = ct_cl_di[0]
#	else:
#		di_as = ct_cl_di[0]+ct_cl_di[1]
		
#	if ct_cl_di[0]=='0':
#		di_as = 1

	
#	return int(di_as)

#stock_partial_picking()

