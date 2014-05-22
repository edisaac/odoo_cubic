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

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def _get_picking_from_pos_order(self, cr, uid, ids, context=None):
        res = {}
        for order in self.pool.get('pos.order').browse(cr,uid,ids,context=context):
            res[order.picking_id.id] = True
        return res.keys()

    def _pos_order_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for i in ids:
            res[i] = False
        order_obj = self.pool.get('pos.order')
        order_ids = order_obj.search(cr, uid, [('picking_id','in',ids)],context=context)
        for order in order_obj.browse(cr, uid, order_ids, context=context):
            res[order.picking_id.id] = order.id
        return res

    _columns = {
            'pos_order_id': fields.function(_pos_order_id,type='many2one',obj='pos.order',
                        method=True,string='POS Order',readonly=True,store={'pos.order':(_get_picking_from_pos_order,['picking_id'],10)}),
        }
        
stock_picking()
