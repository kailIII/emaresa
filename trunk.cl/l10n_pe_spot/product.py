# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
		'spot_product_type' : fields.selection(lambda s,c,u,context={}:s.pool.get('base.element').get_selection(c,u,'PE.SPOT.ANEXO_04',context=c),
                                     'SPOT Product Type',help="kind of goods and services subjected to SPOT (detractions) - SUNAT"),
    }

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'spot_product_type' : fields.selection(lambda s,c,u,context={}:s.pool.get('base.element').get_selection(c,u,'PE.SPOT.ANEXO_04',context=c),
                                     'SPOT Product Type',help="kind of goods and services subjected to SPOT (detractions) - SUNAT"),
    }
