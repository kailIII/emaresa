# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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
    "name": "SUNAT SPOT Management",
    "version": "1.0",
    "description": """
Management of Payment System Tax Obligations with the Central Government (SPOT)

Gestión del Sistema de Pago de Obligaciones Tributarias con el Gobierno Central – SPOT (Sistema de Detracciones) 

    """,
    "author": "Cubic ERP",
    "website": "http://cubicERP.com",
    "category": "Finance",
    "depends": [
            "base_table",
            #"l10n_pe_base",
            "account_transfer_invoice",
			],
	"data":[
			"data/base.table.csv",
            "data/base.element.csv",
            "product_view.xml",
            "account_view.xml",
            "partner_view.xml",
            "company_view.xml",
            "res_config_view.xml",
            "account_data.xml",
            "partner_data.xml",
			],
    "demo_xml": [
			],
    "active": False,
    "installable": True,
}