# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Cubic ERP - Teradata SAC. (http://cubicerp.com).
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
    'name': 'Delivery for Point Of Sale',
    'version': '1.0.0',
    'category': 'Point Of Sale',
    "sequence": 6,
    'description': """
This module allow to make deliverys from POS Backend.
    """,
    'author': 'Cubic ERP',
    'images': [ ],
    'depends': [
            'sale',
            'point_of_sale',
            'delivery',
            'stock',
            'stock_journal_extension',
            'delivery_routes',
            'pos_invoicing'
    ],
    'init_xml': [],
    'update_xml': [
            'wizard/delivery_pos_order_view.xml',
            'wizard/pos_picking_view.xml',
            'wizard/pos_greeting_view.xml',
            'wizard/fill_picking.xml',
            'point_of_sale_view.xml',
            'delivery_view.xml',
            'stock_view.xml',
    ],
    'demo_xml': [
        
    ],
    'test': [
        
    ],
    'installable': True,
    'application': False,
    'certificate' : '',
    # Web client
    'js': [ ],
    'css': [ ],
    'qweb': [ ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
