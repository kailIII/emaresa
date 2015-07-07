# -*- encoding: utf-8 -*-
#
# OpenERP Rent - Renting Module
# Copyright (C) 2010-2011 Thibaut DIRLIK <thibaut.dirlik@gmail.com>
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

import time
import logging
import math
import netsvc
import datetime

from dateutil.relativedelta import *

# OpenLib is a library I wrote for OpenERP, you can download it here :
# https://github.com/WE2BS/openerp-openlib
from openlib.orm import *
from openlib.tools import *

from osv import osv, fields
from tools.translate import _
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from decimal_precision import get_precision

_logger = logging.getLogger('rent')

STATES = (
    ('draft', 'Quotation'), # Default state
    ('confirmed', 'Confirmed'), # Confirmed, have to generate invoices
    ('ongoing', 'Ongoing'), # Invoices generated, waiting for confirmation
    ('billable','Billable'), # Nuevo estado para facturable
    ('done', 'Done'), # All invoices have been confirmed
    ('cancelled', 'Cancelled'), # The order has been cancelled
)

PRODUCT_TYPE = (
    ('rent', 'Rent'),
    ('service', 'Service'),
)

class RentOrder(osv.osv, ExtendedOsv):

    # A Rent Order is almost like a Sale Order except that the way we generate invoices
    # is really different, and there is a notion of duration. I decided to not inherit
    # sale.order because there were a lot of useless things for a Rent Order.

    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, rent_line_ids, context=None):
	context = context or {}
	if not pricelist_id:
		return {}
	value = {
		'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
	}
	if not rent_line_ids:
		return {'value': value}
	warning = {
		'title': _('Pricelist Warning!'),
		'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
	}
	return {'warning': warning, 'value': value}
    
    def on_client_changed(self, cr, uid, ids, client_id, context=None):

        """
        Called when the client has changed : we update all addresses fields :
        Order address, invoice address and shipping address.
        """
        result = {}
	if not client_id:
		return { 'value': result}

	part = self.pool.get('res.partner').browse(cr, uid, client_id, context=context)
	pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
	
	if not part.street:
		raise osv.except_osv (_('Client has not street'), _('You must define the street for this client.'))

       	result = {
		'street' : part.street,
	}

        if part.property_account_position.id:
		result['fiscal_position'] = part.property_account_position.id #client.property_account_position.id

	if pricelist:
		result['pricelist_id'] = pricelist

        return { 'value' : result }


    def on_draft_clicked(self, cr, uid, ids, context=None):

        """
        This method is called when the rent order is in cancelled state and the user clicked on 'Go back to draft'.
        """

        orders = self.filter(ids)
        wkf_service = netsvc.LocalService("workflow")
        self.write(cr, uid, ids, {'state' : 'draft'})

        for order in orders:
            # Delete and re-create the workflow
            wkf_service.trg_delete(uid, 'rent.order', order.id, cr)
            wkf_service.trg_create(uid, 'rent.order', order.id, cr)

        for id, name in self.name_get(cr, uid, ids):
            self.log(cr, uid, order.id, _('The Rent Order "%s" has been reset.') % name)

        return True
    
    def action_show_invoices(self, cr, uid, ids, context=None):

        """
        Show the invoices which have been generated.
        """

        order = self.get(ids[0])

        if not order.invoices_ids:
            raise osv.except_osv(_("No invoices"), _("This rent order has not any invoices."))

        action = {
            'name': '%s Invoice(s)' % order.reference,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': [('origin', '=', order.reference)],
            'context' : {'form_view_ref' : 'account.invoice_form'}
        }

        if len(order.invoices_ids) == 1:
            action['res_id'] = order.invoices_ids[0].id
            action['view_mode'] = 'form,tree'
        
        return action

    
    def on_generate_invoices_clicked(self, cr, uid, ids, context=None):

        """
        Trigger the cron job which generates the invoices when the user clicks on the button.
        """

        self.run_cron_make_invoices(cr, uid, context)
       
        return True

    
##############################################################################################################################
###################											######################
###################			Agregado para finalizar el arriendo				######################
###################											######################
##############################################################################################################################
    def billable_to_done(self, cr, uid, ids, context=None):

#        """
#        Trigger the cron job which generates the invoices when the user clicks on the button and change the state to done.
#        """

        self.run_cron_finish_invoice(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state' : 'done'})
       
        return True
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
##############################################################################################################################


    def action_confirmed(self, cr, uid, ids):

        """
        Called when the workflow goes to confirmed. Currently, the module only handles stockable/consummable products.
        """
	
        line_ids = self.pool.get('rent.order.line').search(cr, uid,[('order_id','=',ids[0])])
	self.pool.get('rent.order.line').write(cr, uid, line_ids, {'state' : 'confirmed'})
        self.write(cr, uid, ids, {'state' : 'confirmed'})
        
        return True

    
    def action_confirmed_service(self, cr, uid, ids):

        """
        Called when the workflow is confirmed and we rent only services products.
        """

        self.write(cr, uid, ids, {'state' : 'confirmed'})
        
        return True

    
    def action_generate_out_move(self, cr, uid, orders_ids):

        """
        Create the stock moves of the specified orders objects. For each order, two picking are created :
            - An output picking, to send the product to the customer.
            - An input picking, to get the products back.
        """

        orders = self.filter(orders_ids)
        move_pool, picking_pool = map(self.pool.get, ('stock.move', 'stock.picking'))
	sequence_obj = self.pool.get('ir.sequence')
        workflow = netsvc.LocalService("workflow")

        for order in orders:
            if order.out_picking_id:
                _logger.warning("Trying to create out move whereas it already exists.")
                continue

            out_picking_id = False

            warehouse_stock_id = order.shop_id.warehouse_id.lot_stock_id.id
            if order.partner_id.property_stock_customer.id:
                customer_output_id = order.partner_id.property_stock_customer.id
            else:
                customer_output_id = order.shop_id.warehouse_id.lot_output_id.id

            for line in order.rent_line_ids:
                if line.product_id.product_tmpl_id.type not in ('product', 'consu'):
                    _logger.info("Ignored product %s, not stockable." % line.product_id.name)
                    continue

                # We create picking only if there is at least one product to move.
                # That's why we do it after checking the product type, because it could be
                # service rent only.
                if not out_picking_id:
                    out_picking_id = picking_pool.create(cr, uid, {
			'name': sequence_obj.get(cr, uid, 'stock.picking.out'),
                        'origin' : order.reference,
                        'type' : 'out',
                        'state' : 'auto',
                        'move_type' : 'direct',
                        'invoice_state' : 'none',
			'rent_id': order.id,
                        'date' : fields.date.today(),
#                        'address_id' : order.partner_shipping_address_id.id,
                        'company_id' : order.company_id.id,
                        'partner_id' : order.partner_id.id
                    })

                # Out move: Stock -> Client
                move_pool.create(cr, uid, {
                    'name': line.description,
                    'picking_id': out_picking_id,
                    'product_id': line.product_id.id,
		    'rent_line_id': line.id,
                    'date': fields.date.today(),
                    'date_expected': line.date_begin_rent,
                    'product_qty': line.quantity,
                    'product_uom': line.product_id_uom.id,
                    'product_uos' : line.product_id_uom.id,
                    'product_uos_qty' : line.quantity,
#                    'address_id': order.partner_shipping_address_id.id,
                    'location_id': warehouse_stock_id,
                    'location_dest_id' : customer_output_id,
                    'state': 'draft',
                })

            # Confirm picking orders
            if out_picking_id:
                workflow.trg_validate(uid, 'stock.picking', out_picking_id, 'button_confirm', cr)
                self.write(cr, uid, order.id, {'out_picking_id' : out_picking_id}),

                # Check assignement (FIXME: This should be optional)
                picking_pool.action_assign(cr, uid, [out_picking_id])

        return True

    
    def action_ongoing(self, cr, uid, ids):

        """
        We switch to ongoing state when the out picking has been confirmed.
        We have to generate the input picking.
        """

###################### DESCOMENTAR AL TERMINAR EL MODULO PARA CREACION DE MOVIMIENTOS AL COMPLETAR LA ENTREGA ####################
#        orders = self.filter(ids)
#        picking_pool, move_pool = map(self.pool.get, ('stock.picking', 'stock.move'))
#	sequence_obj = self.pool.get('ir.sequence')
#        workflow = netsvc.LocalService("workflow")

#        for order in orders:
#            in_picking_id = picking_pool.create(cr, uid, {
#		'name': sequence_obj.get(cr, uid, 'stock.picking.in'),
#                'origin' : order.out_picking_id.origin,
#                'type' : 'in',
#                'state' : 'auto',
#                'move_type' : 'direct',
#		'rent_id': order.id,
#                'invoice_state' : 'none',
#                'date' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                #'address_id' : order.partner_shipping_address_id.id,
#                'company_id' : order.company_id.id,
#		'partner_id' : order.partner_id.id
#            })
#            for line in order.out_picking_id.move_lines:
#                move_pool.create(cr, uid, {
#                    'name': line.name,
#                    'picking_id': in_picking_id,
#                    'product_id': line.product_id.id,
#                    'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                     #'date_expected': order.date_in_shipping,    ###### Organizar para facturacion
#                    'product_qty': line.product_qty,
#                    'product_uom': line.product_uom.id,
#                    'product_uos' : line.product_uos.id,
#                    'product_uos_qty' : line.product_uos_qty,
#                    'address_id': line.address_id.id,
#                    'location_id': line.location_dest_id.id,
#                    'location_dest_id' : line.location_id.id,
#                    'state': 'draft',
#		    'rent_line_id': line.rent_line_id.id
#                })
            
#            self.write(cr, uid, order.id, {'in_picking_id' : in_picking_id})
            
            # Confirm the picking
#            workflow.trg_validate(uid, 'stock.picking', in_picking_id, 'button_confirm', cr)

            # Check assignement (TODO: This should be optional)
#            picking_pool.action_assign(cr, uid, [in_picking_id])
##################################################################################################################################

#        self.write(cr, uid, ids, {'state' : 'ongoing'})
        self.write(cr, uid, ids, {'state' : 'done'})

        return True

    
    def action_show_shipping(self, cr, uid, ids, type, context=None):

        """
        Open the associated incoming shipment, or raise an error.
        """

        order = self.get(ids[0])

        if type == 'in' and not order.in_picking_id:
            raise osv.except_osv(_('No Incoming Shipment'),
                _("There is no incoming shipment associated to this rent order. It might be a service-only rent order, "
                "or the rent order hasn't been delivered yet.") )
        elif type == 'out' and not order.out_picking_id:
            raise osv.except_osv(_('No Delivery Order'),
                _("There is no delivery order associated to this rent order. It might be a service-only rent order, "
                "or the rent order hasn't been confirmed yet.") )

        value = {
            'name' : 'Incoming Shipment',
            'type' : 'ir.actions.act_window',
            'view_type' : 'form',
            'view_mode' : 'form,tree',
            'res_model' : 'stock.picking',
        }

        if type == 'out':
            value['name'] = 'Delivery Order'
            value['res_id'] = order.out_picking_id.id
        else:
            value['name'] = 'Incoming Shipment'
            value['res_id'] = order.in_picking_id.id
            
        return value

    
    def action_cancel(self, cr, uid, ids):

        """
        If you cancel the order before invoices have been generated, it's ok.
        Else, you can cancel only if invoices haven't been confirmed yet.
        You can't cancel an order which have confirmed picking.
        """

        orders = self.filter(ids)

        for order in orders:

            if order.state in ('draft', 'confirmed', 'ongoing'):
                # Check invoices
                invoice_ids = []
                for invoice in order.invoices_ids:
	            if invoice.state not in ('draft', 'cancel'):
                        raise osv.except_osv(_("You can't cancel this order."),
                            _("This order have confirmed invoice, and can't be deleted right now."))
                    invoice_ids.append(invoice.id)

                # Check stock.picking objects
                shipping_exption = osv.except_osv(_("You can't cancel this order."),
                    _("This order have confirmed shipping orders !"))
                if order.out_picking_id.id and order.out_picking_id.state == 'done':
                    raise shipping_exption
                if order.in_picking_id.id and order.in_picking_id.state == 'done':
                    raise shipping_exption

                # Remove objects associated to this order
                picking_ids = [getattr(order, field).id for field in ('out_picking_id', 'in_picking_id')\
                                if getattr(order, field).id]
                self.write(cr, uid, order.id, {
                    'out_picking_id' : False,
                    'in_picking_id' : False,
                    'invoices_ids' : [(5)],
                    'state' : 'cancelled',
                })

                self.pool.get('account.invoice').unlink(cr, uid, invoice_ids)
                self.pool.get('stock.picking').unlink(cr, uid, picking_ids)
            else:
                raise osv.except_osv(_('Error'), _("You can't cancel an order in this state."))

        return True

    
    def get_order_from_lines(self, cr, uid, ids, context=None):

        """
        Returns lines ids associated to this order.
        """

        lines = self.filter(ids, _object='rent.order.line')
        return [line.order_id.id for line in lines]

    def get_invoiced_rate(self, cr, uid, ids, fields_name, arg, context=None):

        """
        Returns the percentage of invoices which have been confirmed.
        """

        orders = self.filter(ids)
        result = {}

        for order in orders:
            invoices_count = len(order.invoices_ids)
            if not invoices_count:
                result[order.id] = 0
                continue
            invoices_confirmed = len(
                [i for i in order.invoices_ids if i.state in ('open', 'paid')])
            result[order.id] = invoices_confirmed / invoices_count * 100.0
        return result

    
    def get_totals(self, cr, uid, ids, fields_name, arg, context=None):

        """
        Compute the total if the rent order, with taxes.
        """

        result = {}
        tax_pool, fiscal_position_pool = map(self.pool.get, ['account.tax', 'account.fiscal.position'])
        orders = self.filter(ids)

        for order in orders:

            total = 0.0
            total_with_taxes = 0.0
            total_taxes = 0.0
            total_taxes_with_discount = 0.0
            total_buy_price = 0
            total_sell_price = 0

            for line in order.rent_line_ids:
		
                # We map the tax_ids thanks to the fiscal position, if specified.
                tax_ids = line.tax_ids
                if order.fiscal_position.id:
                    tax_ids = tax_pool.browse(cr, uid, fiscal_position_pool.map_tax(
                        cr, uid, order.fiscal_position, tax_ids, context=context),context=context)
                
                # The compute_all function is defined in the account module Take a look.
                prices = tax_pool.compute_all(cr, uid, tax_ids, line.duration_unit_price, line.quantity) 
                total_buy_price += tax_pool.compute_all(cr, uid, tax_ids,
                    line.product_id.product_tmpl_id.standard_price, line.quantity)['total_included']
                total_sell_price += tax_pool.compute_all(cr, uid, tax_ids,
                    line.product_id.product_tmpl_id.list_price, line.quantity)['total_included']

                total += prices['total']
                total_with_taxes += prices['total_included']
                total_taxes += math.fsum([tax.get('amount', 0.0) for tax in prices['taxes']])
                total_taxes_with_discount += math.fsum(
                    [tax.get('amount', 0.0) * (1 - (order.discount or 0.0) / 100.0) for tax in prices['taxes']])

            # We apply the global discount
            total_with_discount = total * (1 - (order.discount or 0.0) / 100.0)
            total_with_taxes_with_discount = total_with_discount + total_taxes_with_discount

            # TODO: When implementing priceslist, we will have to use currency.round() to round these numbers
            result[order.id] = {
                'total' : total,
                'total_with_taxes' : total_with_taxes,
                'total_taxes' : total_taxes,
                'total_taxes_with_discount' : total_taxes_with_discount,
                'total_with_discount' : total_with_discount,
                'total_with_taxes_with_discount' : total_with_taxes_with_discount,
                'total_products_buy_price' : total_buy_price,
                'total_products_sell_price' : total_sell_price,
            }

        return result

    
    def get_invoice_comment(self, cr, uid, order, date, current, max, period_begin, period_end):

        """
        This method must return a comment that will be added to the invoice.
        """

        # We use the lang of the partner instead of the lang of the user to put the text into the invoice.
        partner_lang = self.get(code=order.partner_id.lang, _object='res.lang')
        context = {'lang' : order.partner_id.lang}

        datetime_format = partner_lang.date_format + _(' at ') + partner_lang.time_format
        datetime_format = datetime_format.encode('utf-8')
        date_format = partner_lang.date_format
        date_format = date_format.encode('utf-8')

        begin_date = to_datetime(order.date_begin_rent).strftime(datetime_format).decode('utf-8')
        end_date = to_datetime(order.date_end_rent).strftime(datetime_format).decode('utf-8')

        try:
            period_begin = to_datetime(period_begin).strftime(datetime_format).decode('utf-8')
            period_end = to_datetime(period_end).strftime(datetime_format).decode('utf-8')
        except ValueError:
            period_begin = to_date(period_begin).strftime(date_format).decode('utf-8')
            period_end = to_date(period_end).strftime(date_format).decode('utf-8')

        return _(
            "Rental from %s to %s, invoice %d/%d.\n"
            "Invoice for the period from %s to %s."
        ) % (
            begin_date,
            end_date,
            current,
            max,
            period_begin,
            period_end,
        )

    
    def get_invoice_at(self, cr, uid, order, data):

        """
        Generates an invoice at the specified date. The two last arguments current and max
        defines the maximum number of invoices and the current invoice number. For example: current=4, max=12.
        """

        invoice_pool, invoice_line_pool = self.get_pools('account.invoice', 'account.invoice.line')

        # We create a "fake" context variable which contains the customer language language to translate
        # the invoice name correctly.
        context = {'lang' : order.partner_id.lang}

        # Create the invoice
        invoice_date_str = data['date'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_period_begin_str = data['period_begin'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_period_end_str = data['period_end'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        invoice_id = invoice_pool.create(cr, uid,
            {
                'name' : _('Invoice %d/%d') % (data['invoice_number'], data['invoice_count']),
                'origin' : order.reference,
                'type' : 'out_invoice',
                'state' : 'draft',
                'date_invoice' : invoice_date_str,
                'partner_id' : order.partner_id.id,
#                'address_invoice_id' : order.partner_invoice_address_id.id,
                'account_id' : order.partner_id.property_account_receivable.id,
                'fiscal_position' : order.fiscal_position.id,
		#############################################################################################
#                'comment' : self.get_invoice_comment(
#                   cr, uid, order, invoice_date_str, data['invoice_number'], data['invoice_count'],
#                   invoice_period_begin_str, invoice_period_end_str),
		#############################################################################################
            }
        )

        # Create the lines
        lines_ids = [line.id for line in order.rent_line_ids]
        lines_data = self.pool.get('rent.order.line').get_invoice_lines_data(cr, uid, lines_ids,
            data['price_factor'], first_invoice=(data['invoice_number'] == 1))

        for line_data in lines_data:
            line_data['invoice_id'] = invoice_id
            invoice_line_pool.create(cr, uid, line_data)

        # Update taxes
        invoice_pool.button_reset_taxes(cr, uid, [invoice_id])

        return invoice_id

    
    def get_invoice_for_once_period(self, cr, uid, order, context=None):

        """
        Generates only one invoice (at the end of the rent).
        """

        return [{
            'date' : to_datetime(order.date_begin_rent).date(),
            'invoice_number' : 1,
            'invoice_count' : 1,
            'period_begin' : to_datetime(order.date_begin_rent),
            'period_end' : to_datetime(order.date_end_rent),
            'price_factor' : 1.0
        }]
    
    def get_invoices_for_month_period(self, cr, uid, order, context=None):

        """
        Generates an invoice for each month of renting. Invoices dates are based on the begin date.
        For example, renting a produt from the January 15 for 3 months, will make 3 invoices :
            - January 15th (First) (Period January 15th to Febuary 14th)
            - Febuary 15th (Second) (Period Febuary 15th tu March 14th)
            - March 15th (Last) (Period March 15th to April 14th)
        """

        uom_month = self.get(category_id__name='Duration', name='Month', _object='product.uom')
       # uom_year = self.get(category_id__name='Duration', name='Year', _object='product.uom')

#        if order.rent_duration_unity.id not in (uom_month.id, uom_year.id):
#            raise osv.except_osv(_("Invalid duration unity"),
#                _("You must use a Month or Year unity with a Monthly invoicing period."))

        order_duration_in_month = int(self.pool.get('product.uom')._compute_qty(cr, uid, order.rent_duration_unity.id,
            order.rent_duration, uom_month.id))
        order_begin_date = to_datetime(order.date_begin_rent).date()

        if order_duration_in_month < 2:
            raise osv.except_osv(_("Invalid invoice period"),
                _("You can't use a monthly invoice period if the rent duration is less than 2 months. "
                  "Use the 'Once' period in this case."))

        current_invoice_date = order_begin_date
        result = []

        raise osv.except_osv(_("uh312i1d"),_(str(order_duration_in_month)+"\n"+str(order.rent_duration)))
        # The line price factor is applied on each invoice line. For example, if we make 12 invoices for a
        # rent duration of 1 Year, the price factor will be 12 : Each line price will be divided by 12.
        #
        # We have to do this because the unit price of the product is expressed in the order duration unity,
        # so if the unit price of a product is 1200€/Year, each line unit price is by default 1200. Without the
        # factor, we would have 12 invoices at 1200€ !
        #
        # In the case of a price expressed in month, there is no problem, and the factor is just 1.
        line_price_factor = 1.0
#        if order.rent_duration_unity.id == uom_year.id:
#           line_price_factor = 12.0 * order.rent_duration

        raise osv.except_osv(_("Iqbwhhbqwhiqwe"),_("sdjhabhsdabhsjdbhasd"))
        for i in range(1, order_duration_in_month+1):

            # The date of the next invoice the date of the current one + 1 month
            next_invoice_date = current_invoice_date + relativedelta(months=1)

            # The end of the current period is the date of the next invoice - 1 day
            period_end = (next_invoice_date - relativedelta(days=1))

            current_invoice_data = {
                'date' : current_invoice_date,
                'invoice_number' : i,
                'invoice_count' : order_duration_in_month,
                'period_begin' : current_invoice_date,
                'period_end' : period_end,
                'price_factor' : line_price_factor,
            }
            current_invoice_date = next_invoice_date
            result.append(current_invoice_data)

        return result

    
    def test_have_invoices(self, cr, uid, ids, *args):

        """
        Method called by the workflow to test if the order have invoices.
        """

        return len(self.get(ids[0]).invoices_ids) > 0


    def on_compute_clicked(self, cr, uid, ids, context=None):
	return True
    

    def test_out_shipping_done(self, cr, uid, ids, *args):

        """
        Called by the workflow. Returns True once the product has been output shipped.
        """

        order = self.get(ids[0])

        if not order.out_picking_id: # Service only rent order
            return False

        lines = self.get(ids[0]).out_picking_id.move_lines or []
        return all(line.state == 'done' for line in lines)

    
    def test_in_shipping_billable(self, cr, uid, ids, *args):

        """
        Called by the workflow. Returns True once the product has been input shipped.
        """

        order = self.get(ids[0])
        if not order.in_picking_id:
            return False
        return all(line.state == 'done' for line in order.in_picking_id.move_lines)


    def check_have_lines(self, cr, uid, ids, context=None):

        """
        Raises an error if the order have no lines.
        """

        for order in self.filter(ids):
            if len(order.rent_line_ids) == 0:
                return False
        return True
    
    
    def is_service_only(self, cr, uid, ids, field_name, arg, context=None):

        """
        Returns True if the rent order only rent services products.
        """

#        result = {}
 #       for order in self.filter(ids):
 #           result[order.id] = True
 #           for line in order.rent_line_ids:
 #               if line.product_type == 'rent' and line.product_id.type in ('consu', 'product'):
 #                   result[order.id] = False
#        return result
	return False

    
#    def run_cron_start_stop_rents(self, cr, uid, context=None):

#        """
#        This method is run every 5 minutes (by default). It will search for rent orders which have to be started/stopped.
#        This only concerns service-only rent orders, because they are not started by the workflow.
#        """

#        wkf_service = netsvc.LocalService("workflow")
        
        # Orders that need to be started (moved to ongoing state)
#        for order in self.filter(date_begin_rent__le=datetime.datetime.now(), state='confirmed'):
#            wkf_service.trg_validate(uid, 'rent.order', order.id, 'on_force_start_clicked', cr)
#            _logger.info('Started Rent Order %s' % order.reference)

        # Orders that need to be stopped
#        for order in self.filter(date_end_rent__le=datetime.datetime.now(), state='ongoing'):
#            wkf_service.trg_validate(uid, 'rent.order', order.id, 'on_force_stop_clicked', cr)
#            _logger.info('Stopped Rent Order %s.' % order.reference)

    
###### NO SE USA HASTA QUE HALLA FACTURACION MENSUAL, BOTON COMENTADO ######
    def run_cron_make_invoices(self, cr, uid, context=None):

        """
        This cron make invoices that have to be done.
	"""
	return True
        orders = self.filter(Q(state='ongoing')|Q(state='confirmed')|Q(state='billable'))
        orders_invoices_data = self.get_invoices_data(cr, uid, orders, context)

        for order in orders:

            _logger.debug('Checking invoices of rent order %s' % order.reference)

            # This variable contains a list of data used to create invoices of this order
            # Each list entry is a dictionary, check get_invoices_data() for more infos.
            invoices_data = orders_invoices_data.get(order.id, [])

            for invoice_data in invoices_data:
                # For each invoice data, we check if the corresponding invoice has already been created,
                # and we create it if it has to be (Invoice date <= today)
                if invoice_data['date'].strftime(DEFAULT_SERVER_DATE_FORMAT)\
                in [inv.date_invoice for inv in order.invoices_ids]:
                    _logger.debug('Invoice dated %s already exists, skipped', invoice_data['date'])
                    continue

                if invoice_data['date'] <= datetime.date.today():

                    _logger.info('Creating invoice dated %s for rent order %s...',
                        invoice_data['date'], order.reference)

                    invoice_id = self.get_invoice_at(cr, uid, order, invoice_data)
                    self.write(cr, uid, order.id, {'invoices_ids' : [(4, invoice_id)]})

        _logger.debug('Finished rent orders invoice generation')

    
    def test_done(self, cr, uid, ids, context=None):
        """
        Called by the workflow. Returns True once all products has been done.
        """

        order = self.get(ids[0])
        if not order.rent_line_ids:
            return False
        return all(line.state == 'done' for line in order.rent_line_ids)


    def billable_to_done(self, cr, uid, ids, context=None):
	"""
	Genera facturas para lineas
	"""
	sequence_pool, invoice_pool, invoice_line_pool = self.get_pools('ir.sequence', 'account.invoice', 'account.invoice.line')
	order_objs = self.pool.get('rent.order').browse(cr, uid, ids, context=context)
	
	for order in order_objs:
		line_ids = self.pool.get('rent.order.line').search(cr, uid,\
			[('order_id','=',order.id),('state','=','ongoing')], context=context)
		if not line_ids:
			continue
		invoice_id = invoice_pool.create(cr, uid, {
			'name' : sequence_pool.get(cr, uid, 'account.invoice'),
			'origin' : order.reference,
			'type' : 'out_invoice',
			'state' : 'draft',
			'date_invoice' : datetime.datetime.today().date(),
			'partner_id' : order.partner_id.id,
			'account_id' : order.partner_id.property_account_receivable.id,
			'fiscal_position' : order.fiscal_position.id,
		})
		lines_data = self.pool.get('rent.order.line').get_invoice_lines_data(cr, uid, line_ids,\
			 invoice_id, context=context)
		for line_data in lines_data:
			line_data['invoice_id'] = invoice_id
			invoice_line_pool.create(cr, uid, line_data)

		# Update taxes
		invoice_pool.button_reset_taxes(cr, uid, [invoice_id])

		self.write(cr, uid, order.id, {'invoices_ids' : [(4, invoice_id)]})

		if self.test_done(cr, uid, ids, context):
			self.write(cr, uid, order.id, {'state' : 'done'})
	return True

##########################################################################################################################
######################										##########################
######################		Funcion de finalizacion de periodo de arriendo			##########################
######################										##########################
##########################################################################################################################
    def run_cron_finish_invoice(self, cr, uid, ids, context=None):

        """
        This cron make invoices that have to be done.
	"""
	return True
###### LINEAS DE LAS ORILLAS COMENTADAS PARA QUE PASE Y FINALIZE EL MODULO ######
       #orders = self.filter(Q(state='billable'))
       #orders = self.filter(Q(state='ongoing')|Q(state='confirmed')|Q(state='billable'))

	order = self.pool.get('rent.order').browse(cr, uid, ids, context=context)[0]
	lines_ids = self.pool.get('rent.order.line').search(cr, uid, [('order_id','=',order.id)])
	lines = self.pool.get('rent.order.line').browse(cr, uid, lines_ids, context=context)

	a = order.partner_id.property_account_receivable.id
	if order.partner_id and order.partner_id.property_payment_term.id:
		pay_term = order.partner_id.property_payment_term.id
	else:
		pay_term = False
	inv = {
		'name': order.reference,
		'origin': order.reference,
		'type': 'out_invoice',
		'reference': "P%dALQ%d" % (order.partner_id.id, order.id),
		'account_id': a,
		'partner_id': order.partner_id.id,
		'invoice_line': [(6, 0, lines.PARSEAR)],
		'currency_id' : order.pricelist_id.currency_id.id,
		'comment': order.description,
		'payment_term': pay_term,
		'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
		'user_id': order.salesman and order.salesman.id or False,
		'company_id': order.company_id and order.company_id.id or False,
		'date_invoice': fields.date.today(),
	}
	inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
	raise osv.except_osv(('Error!'),(str(inv_id)))
        orders_invoices_data = self.get_invoices_data(cr, uid, orders, context)
        for order in orders:

            _logger.debug('Checking invoices of rent order %s' % order.reference)

            # This variable contains a list of data used to create invoices of this order
            # Each list entry is a dictionary, check get_invoices_data() for more infos.
            invoices_data = orders_invoices_data.get(order.id, [])
            for invoice_data in invoices_data:

                # For each invoice data, we check if the corresponding invoice has already been created,
                # and we create it if it has to be (Invoice date <= today)
                if invoice_data['date'].strftime(DEFAULT_SERVER_DATE_FORMAT)\
                in [inv.date_invoice for inv in order.invoices_ids]:
                    _logger.debug('Invoice dated %s already exists, skipped', invoice_data['date'])
                    continue

                if invoice_data['date'] <= datetime.date.today() :
		    raise osv.except_osv(_('Error !'), _("holi ;)"))
                    _logger.info('Creating invoice dated %s for rent order %s...',
                        invoice_data['date'], order.reference)

                    invoice_id = self.get_invoice_at(cr, uid, order, invoice_data)
                    self.write(cr, uid, order.id, {'invoices_ids' : [(4, invoice_id)]})

        _logger.debug('Finished rent orders invoice generation')

	return True
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


    
    def check_period_and_unity(self, cr, uid, ids, context=None):

        """
        This checks that the unity is valid for the invoicing period, for example :
            Day is a not a valid duration unity for a Month invoicing.
        """

        for order in self.filter(ids):
            if order.rent_duration_unity in order.rent_invoice_period.not_allowed_duration_unities:
                return False
        return True

    
    def copy(self, cr, uid, id, default=None, context=None):

        """
        We have to generate a new reference when we copy the object.
        """

        if not default:
            default = {}

        default.update({
            'state': 'draft',
            'invoices_ids': [],
            'out_picking_id': False,
            'in_picking_id' : False,
            'reference': self.pool.get('ir.sequence').get(cr, uid, 'rent.order'),
        })
        
        return super(RentOrder, self).copy(cr, uid, id, default, context=context)

    
    def unlink(self, cr, uid, ids, context=None):

        """
        Avoid removing done/ongoing rent orders.
        """

        for order in self.filter(ids):
            if order.state in ('ongoing', 'done'):
                raise osv.except_osv(_('Error'), _("You can't remove an ongoing/done rent order."))
        return super(RentOrder, self).unlink(cr, uid, ids, context)

    def _date(self, cr, uid, ids, context=None):
	return (datetime.datetime.today() - datetime.timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")


    def _get_default_shop(self, cr, uid, context=None):
	company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
	shop_ids = self.pool.get('sale.shop').search(cr, uid, [('company_id','=',company_id)], context=context)
	if not shop_ids:
		raise osv.except_osv(_('Error!'), _('There is no default shop for the current user\'s company!'))
	return shop_ids[0]


    _name = 'rent.order'
    _rec_name = 'reference'
    _order = 'reference DESC'

    _columns = {
        'state' : fields.selection(STATES, 'State', readonly=True, help=
            'Gives the state of the rent order :\n'
            '- Quotation\n- Confirmed\n- Ongoing (Products have been shipped)\n'
            '- Billable\n - Done (Products have been get back)'),
        'reference' : fields.char('Reference', size=128, required=True, readonly=True,
		help='The reference is a unique identifier that identify this order.'),
        'origin_document':fields.char('Origin Document', size=128, required=True),
        'date_created' : fields.datetime('Date', required=True, readonly=True,
		help='Date of the creation of this order.'),
        'shop_id':fields.many2one('sale.shop', 'Shop', required=True, readonly=True,
	    help='The shop where this order was created.', ondelete='RESTRICT'),
	'company_id':fields.many2one('res.company', 'Company', required=True, readonly=False),
        'partner_id':fields.many2one('res.partner', 'Customer', required=True, change_default=True,
            domain=[('customer', '=', 'True')], context={'search_default_customer' : True},
            readonly=False,#True, states={'draft' : [('readonly', False)]}, 
	    ondelete='RESTRICT', help='Select a customer. Only partners marked as customer will be shown.'),

#        'partner_invoice_address_id': fields.many2one('res.partner.address', 'Invoice Address', readonly=True,
#            required=True, states={'draft': [('readonly', False)]}, ondelete='RESTRICT', help=
#            'Invoice address for current Rent Order.'),
#        'partner_order_address_id': fields.many2one('res.partner.address', 'Ordering Address', readonly=True,
#            required=True, states={'draft': [('readonly', False)]}, ondelete='RESTRICT', help=
#            'The name and address of the contact who requested the order or quotation.'),
#        'partner_shipping_address_id': fields.many2one('res.partner.address', 'Shipping Address', readonly=True,
#            required=False,# states={'draft': [('readonly', False)]}, 
#	    ondelete='RESTRICT', help='Shipping address for current rent order.'),

        'salesman' : fields.many2one('res.users', 'Salesman', ondelete='SET NULL', readonly=True, 
	    	help='The salesman who handle this order, optional.'),
        'rent_line_ids' : fields.one2many('rent.order.line', 'order_id', 'Order Lines', readonly=True, required=True,
	   	help='Lines of this rent order.'),
	'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True,
		# states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
		 help="Pricelist for current rent order."),
        'notes': fields.text('Notes', help='Enter informations you want about this order.'),
	#asdasdasdasdasd no sale en la vista.
        'discount' : fields.float('Global discount (%)', readonly=True,
	#states={'draft': [('readonly', False)]},
	    	help='Apply a global discount to this order.'),
        'fiscal_position' : fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=True,
	    ondelete='SET NULL', help='Fiscal Position applied to taxes and accounts.'),
        'invoices_ids':fields.many2many('account.invoice', 'rent_order_invoices', 'rent_order_id', 'invoice_id',
            'Invoices', readonly=True),
        'invoiced_rate' : fields.function(get_invoiced_rate, string='Invoiced', help=
            'Invoiced percent, calculated on the number if invoices confirmed.', method=True),
        'out_picking_id' : fields.many2one('stock.picking', 'Output picking id', help=
            'The picking object which handle Stock->Client moves.', ondelete='RESTRICT'),
        'in_picking_id' : fields.many2one('stock.picking', 'Input picking id', help=
            'The picking object which handle Client->Stock moves.', ondelete='RESTRICT'),
        'description' : fields.char('Object', size=255, help=
            'A small description of the rent order. Used in the report.'),
	    ############################pasar a las lineas#############################
#        'is_service_only' : fields.function(is_service_only, method=True, type="boolean", string="Is service only", help=
 #           "True if the rent order only rent services products.", store={
  #              'rent.order.line' : (get_order_from_lines, ['product_id'], 10),
   #             'rent.order' : (lambda *a: a[3], None, 10),
   #         }),
   ######pasarlo a las lineas#########################################
        'total' : fields.function(get_totals, multi='totals', method=True, type="float",
            string="Untaxed amount", digits_compute=get_precision('Sale Price'),\
            store={
                'rent.order.line':(get_order_from_lines, ['rent_duration','quantity'], 8),
                'rent.order':(lambda *a: a[3], ['state'], 10),
            }),
        'total_with_taxes' : fields.function(get_totals, multi='totals', method=True, type="float",
            string="Total", digits_compute=get_precision('Sale Price'),\
            store={
                'rent.order.line':(get_order_from_lines, ['rent_duration','quantity'], 8),
                'rent.order':(lambda *a: a[3], ['state'], 10),
            }),
        'total_taxes' : fields.function(get_totals, multi='totals', method=True, type="float",
            string="Taxes", digits_compute=get_precision('Sale Price'),\
            store={
                'rent.order.line':(get_order_from_lines, ['rent_duration','quantity'], 8),
                'rent.order':(lambda *a: a[3], ['state'], 10),
            }),
        'total_with_discount':fields.function(get_totals, multi='totals', method=True, type="float",
            string="Untaxed amount (with discount)", digits_compute=get_precision('Sale Price'),\
            store={
                'rent.order.line':(get_order_from_lines, ['rent_duration','quantity'], 8),
                'rent.order':(lambda *a: a[3], ['state'], 10),
            }),
        'total_taxes_with_discount' : fields.function(get_totals, multi='totals', method=True, type="float",
            string="Taxes (with discount)", digits_compute=get_precision('Sale Price'),\
            store={
                'rent.order.line':(get_order_from_lines, ['rent_duration','quantity'], 8),
                'rent.order':(lambda *a: a[3], ['state'], 10),
            }),
        'total_with_taxes_with_discount' : fields.function(get_totals, multi='totals', method=True, type="float",
            string="Total (with discount)", digits_compute=get_precision('Sale Price'),\
            store={
                'rent.order.line' : (get_order_from_lines, ['rent_duration','quantity'], 8),
                'rent.order' : (lambda *a: a[3], ['state'], 10),
            }),
        'total_products_buy_price' : fields.function(get_totals, multi='totals', type="float",
            string='Products buy price', method=True, digits_compute=get_precision('Sale Price'),\
            store={
		'rent.order.line' : (get_order_from_lines, ['rent_duration', 'quantity'], 8),
	    }),

        'total_products_sell_price' : fields.function(get_totals, multi='totals', type="float",
            string='Products sell price', method=True, digits_compute=get_precision('Sale Price'),\
            store={
		'rent.order.line' : (get_order_from_lines, ['rent_duration', 'quantity'], 8),
	    }),
    }

    _defaults = {
        'date_created': _date,
        'state': 'draft',
        'salesman': # Default salesman is the curent user
            lambda self, cr, uid, context: uid,
        'reference': # The ref sequence is defined in sequence.xml (Default: RENTXXXXXXX)
            lambda self, cr, uid, context:
                self.pool.get('ir.sequence').get(cr, uid, 'rent.order'),
	# Agregado para poner la compañia del usuario.
        'shop_id': _get_default_shop,
	'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid,'rent.order', context=c),
        'discount' : 0.0,
    }

    ########################## Agregado para solucionar problema de related ###########################################
    def company_load(self, cr, uid, ids, company_id, context=None):
	return { 'value':{'company_id':company_id} }
    ###################################################################################################################

    _constraints = [
#        (check_period_and_unity, "You can't use this duration unity with this invoicing period !", ['rent_duration_unity']),
    ]

    _sql_constraints = [
        ('ref_uniq', 'unique(reference)', 'Rent Order reference must be unique !'),
        ('valid_discount', 'check(discount >= 0 AND discount <= 100)', 'Discount must be a value between 0 and 100.'),
    ]
RentOrder()






class RentOrderLine(osv.osv, ExtendedOsv):

    """
    Rent order lines define products that will be rented.
    """

    
    def on_product_changed(self, cr, uid, ids, product_id, quantity):

        """
        This method is called when the product changed :
            - Fill the tax_ids field with product's taxes
            - Fill the description field with product's name
            - Fill the product UoM
        """

        result = {}

        if not product_id:
            return result

        product = self.get(product_id, _object='product.product')

        result['description'] = product.name
        result['tax_ids'] = [tax.id for tax in product.taxes_id]
        result['product_id_uom'] = product.uom_id.id
        result['product_type'] = 'rent' if product.can_be_rent else 'service'

        if result['product_type'] == 'rent':
            result['unit_price'] = product.rent_price
        else:
            result['unit_price'] = product.list_price

        warning = self.check_product_quantity(cr, uid, product, quantity)

        return {'value' : result, 'warning' : warning}

    
    def on_quantity_changed(self, cr, uid, ids, product_id, quantity):

        """
        Checks the new quantity on product quantity changed.
        """

        result = {}
        if not product_id:
            return result
        product = self.get(product_id, _object='product.product')
        if not product.id:
            return result
        warning = self.check_product_quantity(cr, uid, product, quantity)
        return {'value' : result, 'warning' : warning}

    
    def get_order_price(self, line):

        """
        Returns the order price for the line.
        """

        if line.product_type == 'rent':
            return 0.0
        return line.unit_price

    
    def get_rent_price(self, line, duration_unit_price):

        """
        Returns the rent price for the line.
        """

        if line.product_type != 'rent':
            return 0.0

        return duration_unit_price * line.rent_duration

    
    def get_prices(self, cr, uid, ids, fields_name, arg, context):

        """
        Returns the price for the duration for one of this product.
        """

        lines = self.filter(ids)
        result = {}

        for line in lines:
#            if line.product_type == 'rent':
                # We convert the unit price of the product expressed in a unity (Day, Month, etc) into the unity
                # of the rent order. A unit price of 1€/Day will become a unit price of 30€/Month.
#                converted_price = self.pool.get('product.uom')._compute_price(cr, uid,
#                    line.product_id.rent_time_unity.id, line.product_id.rent_price, line.rent_duration_unity.id)
#                real_unit_price = converted_price
#                duration_unit_price = self.get_rent_price(line, converted_price)
#            else:
#                real_unit_price = self.get_order_price(line)
#                duration_unit_price = real_unit_price
	    
	    if not line.order_id.pricelist_id:
		raise osv.except_osv(_('Error!'),_('No Existe una Lista de Precios'))
	    else:
		price = self.pool.get('product.pricelist').price_get(cr, uid, [line.order_id.pricelist_id.id],
				line.product_id.id, line.rent_duration or 1.0, line.order_id.partner_id.id, {
					'uom': line.product_id.rent_time_unity.id,
					'date': line.order_id.date_created
				})[line.order_id.pricelist_id.id]
		if price is False:
			raise osv.except_osv(_('Error!'),_('Cannot find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.'))
		else:
			duration_unit_price = price * line.rent_duration

            # We apply the discount on the unit price
	    duration_unit_price *= (1-line.discount/100.0)

            result[line.id] = {
                'real_unit_price': price,
                'duration_unit_price': duration_unit_price,
                'line_price': duration_unit_price * line.quantity
            }

        return result

    
    def get_invoice_lines_data(self, cr, uid, ids, invoice_id, context=None):
        """
        Returns a dictionary that data used to create the invoice lines.
        """

        rent_lines = self.filter(ids)
	uom_month = self.get(category_id__name='Duration', name='Month', _object='product.uom')
        result = []

        for rent_line in rent_lines:
		# The account that will be used is the income account of the product (or its category)
		invoice_line_account_id = rent_line.product_id.product_tmpl_id.property_account_income.id
		if not invoice_line_account_id:
                	invoice_line_account_id = rent_line.product_id.categ_id.property_account_income_categ.id
		if not invoice_line_account_id:
			raise osv.except_osv(_('Error !'), _('There is no income account defined \
				for this product: "%s" (id:%d)')
				% (rent_line.product_id.name, rent_line.product_id.id,))

		# Calculamos la diferencia de dias entre la ultima facturacion y la fecha de facturacion actual
		invoicing_date = to_datetime(rent_line.invoicing_date)
		last_invoicing_date = to_datetime(rent_line.last_invoicing_date)
		date_in_shipping = to_datetime(rent_line.date_in_shipping)

		delta = invoicing_date - last_invoicing_date
		next_invoice_date = invoicing_date + relativedelta(months=1)

		if date_in_shipping < next_invoice_date:
			next_invoice_date = date_in_shipping
		
		invoice_line_data = {
			'name': rent_line.description,
			'account_id': invoice_line_account_id,
			'price_unit': rent_line.line_price/rent_line.rent_duration * delta.days,
			'quantity': rent_line.quantity,
			'discount': rent_line.discount,
			'product_id': rent_line.product_id.id or False,
			'invoice_line_tax_id': [(6, 0, [x.id for x in rent_line.tax_ids])],
			'note': rent_line.notes,
			'sequence' : 10,
		}

		result.append(invoice_line_data)
		
		# Actualizamos fechas de facturacion de las lineas
		self.pool.get('rent.order.line').write(cr, uid, rent_line.id, {
			'last_invoicing_date': rent_line.invoicing_date,
			'invoicing_date': next_invoice_date
		})
		
		if datetime.datetime.today() >= invoicing_date:
			self.pool.get('rent.order.line').write(cr, uid, rent_line.id, {'state': 'done'})

        return result

    
    def check_product_type(self, cr, uid, ids, context=None):

        """
        Check that the product can be rented if it's makred as 'rent', and that is is
        a service product it it's marked as 'Service' or at least, sellable.
        """

        lines = self.filter(ids)

        for line in lines:
            if line.product_type == 'rent' and not line.product_id.can_be_rent:
                return False
            elif line.product_type == 'service':
                if line.product_id.type != 'service' or not line.product_id.sale_ok:
                    return False
        return True

    
    def check_product_quantity(self, cr, uid, product, quantity):

        """
        This method is not called from a constraint. It checks if there is enought quantity of this product,
        and return a 'warning usable' dictionnary, or an empty one.
        """

        warning = {}
        if product.type != 'product':
            return warning
        if product.qty_available < quantity: # We use the real quantity, not the virtual one for renting !
            warning = {
                'title' : _("Not enought quantity !"),
                'message' : _("You don't have enought quantity of this product. You asked %d, but there are "
                              "%d available. You can continue, but you are warned.") % (quantity, product.qty_available)
            }
        return warning


    def on_duration_changed(self, cr, uid, ids, rent_begin, duration, duration_unity_id, company, context=None):

        """
        This method is called when the duration or duration unity changed. Input shipping date
        is updated to be set at the end of the duration automatically.
        """

        if not rent_begin or not duration or not duration_unity_id:
            return {}
        
        day_unity = self.get(category_id__name='Duration', name='Day', _object='product.uom')
        month_unity = self.get(category_id__name='Duration', name='Month', _object='product.uom')
        year_unity = self.get(category_id__name='Duration', name='Year', _object='product.uom')

        # Converts the order duration (expressed in days/month/years) into the days duration
        if duration_unity_id == day_unity.id:
            delta = relativedelta(days=duration)
        elif duration_unity_id == month_unity.id:
            delta = relativedelta(months=duration)
        elif duration_unity_id == year_unity.id:
            delta = relativedelta(years=duration)
        else:
            raise osv.except_osv(_("Error"), "Unknown duration unity with id %d" % duration_unity_id)

        # Depending of the widget, the begin date can be a date or a datetime
        try:
            begin = to_datetime(rent_begin)
        except ValueError:
            try:
                begin = to_date(rent_begin)
            except ValueError:
                raise osv.except_osv('Begin date have an invalid format.')

        end = (begin + delta)# COMENTO MIENTRAS #- relativedelta(days=1)
		# We remove 1 day to set the return date the same day that the rent end date
        # 'end' can be a datetime or a date object, depending of the widget.
#        end = datetime.datetime.combine(end.date() if isinstance(end, datetime.datetime) else end,
#            to_time(company.rent_afternoon_end))
        end = end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

      	return {'value' : {'date_in_shipping' : end}}


    def correct_date(self, cr, uid, ids, rent_begin, rent_end, tipo):
	"""
		This method is called when the return_date changed. Duration days is updated and set automatically.
	"""
		
	if not rent_begin or not rent_end:
		return {}

	tipo_obj = self.pool.get('product.uom').browse(cr, uid, tipo)

	year_b = rent_begin[:4]
	month_b = rent_begin[5:7]
	day_b = rent_begin[8:10]

	year_e = rent_end[:4]
	month_e = rent_end[5:7]
	day_e = rent_end[8:10]

	cast_begin = datetime.date(int(year_b),int(month_b),int(day_b))
	cast_end   = datetime.date(int(year_e),int(month_e),int(day_e))

	if tipo_obj.name == 'Day':
		cal_dias   = cast_end - cast_begin

		if cal_dias.days == 0:
			dias = 1
		else:
			dias = cal_dias.days

		return {
			'value': {
				'rent_duration' : int(dias)
			}
		}
		
	elif tipo_obj.name == 'Month':
		cal_dias = cast_end - cast_begin
		if cal_dias.days < 30:
			if cast_end.month == 2 and cal_dias.days < 28:
				month = 1
			else:
				month = cal_dias.days/30
		else:
			month = cal_dias.days/30

		return {
			'value': {
				'rent_duration' : int(cal_dias.days)/30
			}
		}
	else: 
		age = cast_end.year - cast_begin.year

		return {
			'value': {
				'rent_duration' : int(age)
			}
		}
		
	
    def get_end_date(self, cr, uid, ids, field_name, arg, context=None):

        """
        Returns the rent order end date, based on the duration and the company configuration
        """

        orders = self.filter(ids)
        result = {}

        for order in orders:

            begin = to_datetime(order.date_begin_rent)
            duration = order.rent_duration
            
            day_unity = self.get(category_id__name='Duration', name='Day', _object='product.uom')
            month_unity = self.get(category_id__name='Duration', name='Month', _object='product.uom')
            year_unity = self.get(category_id__name='Duration', name='Year', _object='product.uom')
            
            # Converts the order duration (expressed in days/month/years) into the days duration
            if order.rent_duration_unity.id == day_unity.id:
                delta = relativedelta(days=duration)
            elif order.rent_duration_unity.id == month_unity.id:
                delta = relativedelta(months=duration)
            elif order.rent_duration_unity.id == year_unity.id:
                delta = relativedelta(years=duration)
            else:
                raise osv.except_osv(_("Error"), "Unknown duration unity: %s" % order.rent_duration_unity.name)

            # Remove one day to have a more realistic duration: In the case of a 1 day duration
            # we except the customer to bring the products the same day, not tomorrow.
            end = (begin + delta) - relativedelta(days=1)
#            end = datetime.datetime.combine(end.date(), to_time(order.company_id.rent_afternoon_end))
            end = end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

            result[order.id] = end

        return result

    
    def default_begin_rent(self, cr, uid, context=None):

        """
        Returns the default begin rent datetime. The user can configure its default behavior in it company :
            - Today: When the rent order is created, the begin date is set to today by defaut, at afternoon.
            - Tomorrow (Morning): When the rent order is created, the begin date is set the tomorrow morning
            - Tomorrow (Afternoon): Same but afternoon
            - Empty: No default values
        """

        now = datetime.datetime.now()
        company = self.get(uid, _object='res.users').company_id

#        rent_afternoon_begin = to_time(company.rent_afternoon_begin)
#        rent_morning_begin = to_time(company.rent_morning_begin)

#        if company.rent_default_begin == 'today':
#           # If we are in the morning, we set the begin at afternoon, else, we set the begin to now
#        if now.time() < rent_afternoon_begin:
#	     begin = datetime.datetime.combine(now.date(), rent_afternoon_begin)
#        else:
#            begin = now
#        elif company.rent_default_begin == 'tomorrow_morning':
#            begin = datetime.datetime.combine(now.date()+datetime.timedelta(days=1), rent_morning_begin)
#        elif company.rent_default_begin == 'tomorrow_after':
#            begin = datetime.datetime.combine(now.date()+datetime.timedelta(days=1), rent_afternoon_begin)
#        else:
#            return False

	return now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    
    def default_duration_unity(self, cr, uid, context=None):

        """
        Returns the 1st UoM present into the Duration category.
        """

        unity = self.get(category_id__name='Duration', _object='product.uom')

        if not unity:
            _logger.warning("It seems that there isn't a reference unity in the 'Duration' UoM category. "
                            "Please check that the category exists, and there's a reference unity.")

        return unity.id if unity else False

    
    _name = 'rent.order.line'
    _rec_name = 'description'
    _columns = {
        'date_begin_rent':fields.datetime('Shipping date', required=True,
            readonly=True, help='Date of the begin of the leasing.'),
        'date_end_rent':fields.function(get_end_date, type="datetime", method=True, string="Rent end date",
            store={ 'rent.order':(lambda self, cr, uid, ids, context: ids, ['rent_duration', 'rent_duration_unity'],10,)}),
        'date_in_shipping':fields.datetime('Return date', readonly=True, required=True,
	    	help='Date of products return.'),
        'last_invoicing_date':fields.datetime('Last invoicing date', readonly=False, required=False,
	    	help='Last invoicing date.'),
        'invoicing_date':fields.datetime('Invoicing date', readonly=True, required=True,
	    	help='Last invoicing date.'),
        'description':fields.char('Description', size=180, required=True, readonly=True,
            help='This description will be used in invoices.'),
        'order_id':fields.many2one('rent.order', 'Order', required=True, ondelete='CASCADE'),
        'product_id':fields.many2one('product.product', _('Product'), required=True, readonly=True,
             context="{'search_default_rent' : True}", domain="[('can_be_rent','=',True)]",
            help='The product you want to rent.'),
        'product_type':fields.selection(PRODUCT_TYPE, 'Type of product', required=True, readonly=True,
            help="Select Rent if you want to rent this product. Service means that you will sell this product "
                "with the others rented products. Use it to sell some services like installation or assurances. "
                "Products which are sold will be invoiced once, with the first invoice."),
        'product_id_uom':fields.related('product_id', 'uom_id', relation='product.uom', type='many2one',
            string='UoM', readonly=True, help='The Unit of Measure of this product.'),
        'quantity':fields.integer('Quantity', required=True, readonly=True,
            help='How many products to rent.'),
        'discount':fields.float('Discount (%)', readonly=True, digits=(16, 2),
            help='If you want to apply a discount on this order line.'),
#        'state':fields.related('order_id', 'state', type='selection', selection=STATES, readonly=True, string='State'),
	'state':fields.selection([('draft','Draft'),
				('confirmed','Confirmed'),
				('ongoing','Ongoing'),
				('done','Done')],'state', readonly=True, required=True),
        'tax_ids':fields.many2many('account.tax', 'rent_order_line_taxes', 'rent_order_line_id', 'tax_id', 'Taxes',
	    readonly=True), 
        'notes':fields.text('Notes'),

        'rent_duration':fields.integer('Duration',
            required=True, readonly=True, help='The duration of the lease, expressed in selected unit.'),
        'rent_duration_unity':fields.many2one('product.uom', string='Duration Unity', domain=[('category_id.name', '=', 'Duration')],
            required=True, readonly=True,
	    help='The duration unity, available choices depends of your company configuration.'),
        'unit_price':fields.float('Product Unit Price', required=True, 
	    help='The price per duration or the sale price, depending of the product type. For rented product, the price '
            'is expressed in the product rent unity, not the order rent unity! BE CAREFUL!'),
        'real_unit_price':fields.function(get_prices, method=True, multi=True, type="float", string="Unit Price",
            help='This price correspond to the price of the product, not matter its type. In the case of a rented '
                 'product, its equal to the unit price expressed in order duration unity, '
                 'and in the case of a service product, to the sale price of the product.'),
        'duration_unit_price':fields.function(get_prices, method=True, multi=True, type="float", string="Duration Unit Price",
            help='The price of ONE product for the entire duration.'),

        'line_price':fields.function(get_prices, method=True, multi=True, type="float", string="Subtotal"),
	'company_id':fields.related('order_id','company_id', type="many2one", relation='res.company', string='Company',\
		store=True, readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'quantity': 1,
        'discount': 0.0,
        'unit_price': 0.0,
        'date_begin_rent': default_begin_rent,
	'last_invoicing_date': default_begin_rent,
        'rent_duration_unity': default_duration_unity,
        'rent_duration': 1,
    }

    _sql_constraints = [
        ('valid_discount', 'check(discount >= 0 AND discount <= 100)', 'Discount must be a value between 0 and 100.'),
        ('valid_price', 'check(unit_price > 0)', 'The price must be superior to 0.')
#        ('begin_after_create', 'check(date_begin_rent >= date_created)', 'The begin date must later than the order date.'),
    ]

    _constraints = [
        (check_product_type, "You can't use this product type with this product. "
            "Check that the product is marked for rent or for sale. Moreover, "
            "Service products must be declared as 'Service' in the product view.", ['product_type']),
    ]

RentOrderLine()
