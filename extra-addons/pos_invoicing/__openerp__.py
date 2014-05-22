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
    'name': 'Invoicing and Extended Point Of Sale',
    'version': '1.0.0',
    'category': 'Point Of Sale',
    "sequence": 6,
    'description': """
This module allow to make invoices, register the tax id (VAT) of customers and others from point of sale.
This make the correlative sequence of the POS entries by each computer conected to a printer.
    """,
    'author': 'Cubic ERP',
    'images': [ ],
    'depends': ['sale','point_of_sale'],
    'init_xml': [],
    'update_xml': [
        'point_of_sale_view.xml',
        'sale_view.xml',
        'account_view.xml',
        'report/report_cash_register_detail_view.xml',
        'stock_view.xml',
        'wizard/pos_receipt_view.xml',
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
