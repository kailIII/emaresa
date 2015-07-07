# -*- coding: utf-8 -*-
##############################################################################
#
# Author: OpenDrive Ltda
# Copyright (c) 2013 Opendrive Ltda
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields, osv

class stock_picking(osv.osv):
	_inherit = 'stock.partial.picking'

	def do_partial(self, cr, uid, ids, context=None):
		assert len(ids) == 1, 'Partial picking processing may only be done one at a time'
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')
		uom_obj = self.pool.get('product.uom')
		partial = self.browse(cr, uid, ids[0], context=context)
		partial_data = {
			'delivery_date' : partial.date
		}
		picking_type = partial.picking_id.type
		for wizard_line in partial.move_ids:
			line_uom = wizard_line.product_uom
			move_id = wizard_line.move_id.id

			#Quantiny must be Positive
			if wizard_line.quantity < 0:
				raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

			#Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
			qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

			if line_uom.factor and line_uom.factor <> 0:
				if qty_in_line_uom <> wizard_line.quantity:
					raise osv.except_osv(_('Warning'), _('The uom rounding does not allow you to ship "%s %s", only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
			if move_id:
				#Check rounding Quantity.ex.
				#picking: 1kg, uom kg rounding = 0.01 (rounding to 10g), 
				#partial delivery: 253g
				#=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
				initial_uom = wizard_line.move_id.product_uom
				#Compute the quantity for respective wizard_line in the initial uom
				qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
				without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
				if qty_in_initial_uom <> without_rounding_qty:
					raise osv.except_osv(_('Warning'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only roundings of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
			else:
				seq_obj_name =  'stock.picking.' + picking_type
				move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
								'product_id': wizard_line.product_id.id,
								'product_qty': wizard_line.quantity,
								'product_uom': wizard_line.product_uom.id,
								'prodlot_id': wizard_line.prodlot_id.id,
								'location_id' : wizard_line.location_id.id,
								'location_dest_id' : wizard_line.location_dest_id.id,
								'picking_id': partial.picking_id.id
							},context=context)
				stock_move.action_confirm(cr, uid, [move_id], context)
			
	###################################################################################################
	##################################### LLAMADO A FUNCION ###########################################
	###################################################################################################
			if (picking_type == 'internal' and wizard_line.move_id.id):
				picking_line_obj = stock_move.browse(cr, uid, wizard_line.move_id.id)
				if picking_line_obj.asset_category_id and picking_line_obj.asset_category_tributario_id:
					stock_move.asset_create(cr, uid,\
						wizard_line.product_id.name,\
						picking_line_obj.picking_id.name,\
						partial.date[:10],\
						wizard_line.product_id.standard_price,\
						picking_line_obj.asset_category_id,\
						picking_line_obj.asset_category_tributario_id,\
						picking_line_obj.picking_id.partner_id.id,\
						picking_line_obj.picking_id.company_id.id,\
						picking_line_obj.picking_id.company_id.currency_id.id, context=None)
	###################################################################################################
	###################################################################################################
				
			partial_data['move%s' % (move_id)] = {
				'product_id': wizard_line.product_id.id,
				'product_qty': wizard_line.quantity,
				'product_uom': wizard_line.product_uom.id,
				'prodlot_id': wizard_line.prodlot_id.id,
			}

			if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
				partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
						product_currency=wizard_line.currency.id)

		stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context)
		return {'type': 'ir.actions.act_window_close'}
stock_picking()

class stock_move(osv.osv):
	_inherit = 'stock.move'
	
	_columns = {
		'asset_category_id':fields.many2one('account.asset.category', 'Asset IFRS Category'),
		'asset_category_tributario_id':fields.many2one('account.asset.category', 'Asset Tributario Category')
	}

	#Agregar partner_id a funcion y period_id
	def asset_create(self, cr, uid, name, code, purchase_date, purchase_value, asset_category_id, asset_category_tributario_id,\
				partner_id, company_id, currency_id, context=None): 
		context = context or {}
		asset_obj = self.pool.get('account.asset.asset')
		
		#Crea activo IFRS
		vals = {
			'name': name,
			'code': code or False,
			'purchase_value': purchase_value,
			'category_id': asset_category_id.id,
			'partner_id': partner_id,
			'company_id': company_id,
			'currency_id': currency_id,
			'purchase_date' : purchase_date,
		}


		changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
		vals.update(changed_vals['value'])
		asset_id = asset_obj.create(cr, uid, vals, context=context)
		if asset_category_id.open_asset:
			asset_obj.validate(cr, uid, [asset_id], context=context)

		#Crea activo tributario
		vals.update({'category_id':asset_category_tributario_id.id})

		changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
		vals.update(changed_vals['value'])
		asset_id = asset_obj.create(cr, uid, vals, context=context)
		if asset_category_tributario_id.open_asset:
			asset_obj.validate(cr, uid, [asset_id], context=context)

		return True
stock_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

