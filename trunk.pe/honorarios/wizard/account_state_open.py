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
from openerp.osv import osv

from openerp import netsvc
from openerp.tools.translate import _

class account_state_open(osv.osv_memory):
    _name = 'account.state.open'
    _description = 'Account State Open'

    def change_inv_state(self, cr, uid, ids, context=None):
        obj_invoice = self.pool.get('account.invoice')
        if context is None:
            context = {}
        if 'active_ids' in context:
            data_inv = obj_invoice.browse(cr, uid, context['active_ids'][0], context=context)
            if data_inv.reconciled:
                raise osv.except_osv(_('Warning!'), _('Invoice is already reconciled.'))
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', context['active_ids'][0], 'open_test', cr)
        return {'type': 'ir.actions.act_window_close'}

account_state_open()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
