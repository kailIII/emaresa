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

from openerp.osv import osv, fields
import time
from datetime import timedelta,date,datetime
from openerp.tools.translate import _ 

class account_journal_code_sii(osv.osv):
   _inherit = 'account.journal'
   _description = 'Agrega código SII y define si los movimientos son Exentos o Afectos a través de los diarios de OpenERP'
   _columns = {
        'code_sii': fields.char('Código SII', size=64),
	'type_tax': fields.selection([('E','Exento'),('A','Afecto')], 'Tipo de Doc. Exento o Afecto', required=True, help="Exento: Si se define que los documentos que pasan por este diario van a ser siempre Exentos.\n" \
                "Afectos: Se define que los documentos que pasan por este diario van a ser siempre Afectos."
        ),
   }

account_journal_code_sii()
