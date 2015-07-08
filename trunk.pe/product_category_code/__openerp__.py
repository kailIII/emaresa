# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
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


{
    "name": "Product Category Code",
    "version": "1.0",
    'category': 'Generic Modules/Inventory Control',
    "depends": ["product"],
    "author": "Agile Business Group & Domsense",
    "description": """This module just adds 'code' field to product category""",
    'website': 'http://www.agilebg.com',
    'init_xml': [],
    'update_xml': [
        'product_view.xml',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}