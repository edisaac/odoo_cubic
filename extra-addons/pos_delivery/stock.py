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
from tools.translate import _

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        if 'address_id' in vals.keys():
            for o in self.browse(cr, uid, isinstance(ids,int) and [ids] or ids, context=context):
                if o.pos_order_id:
                    if o.delivered:
                        raise osv.except_osv(_('Invalid action !'), 
                                        _('Cannot update the picking address which are already delivered !'))
                    else:
                        self.pool.get('pos.order').write(cr,uid,[o.pos_order_id.id],{
                                                            'shiping_address_id':vals['address_id'],
                                                            },
                                                            context=context)
        if 'delivered' in vals.keys():
            for o in self.browse(cr, uid, isinstance(ids,int) and [ids] or ids, context=context):
                if o.pos_order_id and not o.route_line_id:
                    self.pool.get('pos.order').write(cr,uid,[o.pos_order_id.id],{
                                                            'delivered':vals['delivered'],
                                                            },
                                                            context=context)
        return  super(stock_picking, self).write(cr, uid, ids, vals, context=context)

stock_picking()

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    _columns = {
            'pos_order_id': fields.related('picking_id','pos_order_id',type='many2one',relation='pos.order',string='POS Order',readonly=True,store=False),
            'delivery_date': fields.related('picking_id','pos_order_id','greeting_date',type='date',string='Delivery Date',readonly=True,store=False),
            'time_id': fields.related('picking_id','pos_order_id','time_id',type='many2one',relation='delivery.time',string='Delivery Time',readonly=True)
        }

stock_move()
