# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Teradata SAC (<http://cubicerp.com>).
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
    'name' : 'Purchase Bizagi',
    'version' : '1.1',
    'category': 'Purchase Management',
    'images' : ['images/purchase_validation.jpeg'],
    'depends' : ['board','purchase'],
    'author' : 'CubicERP SAC',
    'description': """
Integration with Bizagi
=======================

This module integrate the purchase module with bizagi of Emaresa.
    """,
    'website': 'http://www.cubicerp.com',
    'data': [
        'board_purchase_view.xml',
        'purchase_view.xml',
        'purchase_workflow.xml',
    ],
    'test': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
