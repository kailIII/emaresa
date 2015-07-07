# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Change Value Residual 2",
    "version" : "1.0",
    "author" : "Econube | Pablo Cabezas Jose Pinto",
    "category" : "Account Asset",
    "description" : "Se cambia la funcion value residual, para que busque los montos en account_asset_depreciation_line",
    "init_xml" : ['account_assent.xml',],
    "depends" : ['base','account_asset',],
    "update_xml" : [],
    "active" : False,
    "installable" : True,
}