# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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
    "name": "Peruvian POS Delivery Localization Basics",
    "version": "1.0",
    "description": """
Profile and basics to peruvian POS Order Delivery localization
    """,
    "author": "Cubic ERP",
    "website": "http://cubicERP.com",
    "category": "Localisation/Profile",
    "depends": [
            "l10n_pe_toponyms",
            "point_of_sale",
            "pos_delivery",
        ],
    "data":["point_of_sale_view.xml"],
    "demo_xml": [ ],
    "active": False,
    "installable": True,
    "certificate" : "",
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
