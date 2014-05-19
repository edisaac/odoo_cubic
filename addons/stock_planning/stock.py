# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

class stock_warehouse(osv.osv):
    _name = "stock.warehouse"
    _inherit = 'stock.warehouse'
    _columns = {
		'supply_warehouse_id' : fields.many2one('stock.warehouse','Supply Warehouse',help="Supply warehouse for stock planning"),
		'stock_journal_id' : fields.many2one('stock.journal','Stock Journal Planning',help="Default stock journal for stock planning"),
	}
stock_warehouse()
