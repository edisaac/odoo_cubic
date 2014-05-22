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

from osv import fields, osv
import netsvc
import time
import logging
_logger = logging.getLogger(__name__)

class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        if context is None:
            context = {}
        order_id = context.get('pos_order_id',False)
        #_logger.info('name_get - order_id : %s'%order_id)
        if not order_id:
            res = super(delivery_carrier, self).name_get(cr, uid, ids, context=context)
        else:
            order = self.pool.get('pos.order').browse(cr, uid, order_id, context=context)
            
            currency = order.pricelist_id.currency_id.name or ''
            res = [(r['id'], r['name']+' ('+(str(r['price'] or ''))+' '+currency+')') for r in self.read(cr, uid, ids, ['name', 'price'], context)]
            #_logger.info('res: %s'%res)
        return res

    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        res={}
        if context is None:
            context = {}
        order_id = context.get('pos_order_id',False)
        #_logger.info('get_price - order_id : %s'%order_id)
	
        if not order_id:
            res = super(delivery_carrier, self).get_price(cr, uid, ids, field_name, arg=arg, context=context)
        else:
            grid_obj=self.pool.get('delivery.grid')
            order = self.pool.get('pos.order').browse(cr, uid, order_id, context=context)
            
            for carrier in self.browse(cr, uid, ids, context=context):
                price=False
                carrier_grid=self.grid_get(cr,uid,[carrier.id],order.shiping_address_id.id,context)
                if carrier_grid:
                    price=grid_obj.get_price(cr, uid, carrier_grid, order, time.strftime('%Y-%m-%d'), context)
                else:
                    price = 0.0
                res[carrier.id]=price
        return res
	
    _columns = {
            'price' : fields.function(get_price, string='Price'),
        }
delivery_carrier()

class delivery_grid(osv.osv):
    _name = "delivery.grid"
    _inherit = "delivery.grid"

    def get_price(self, cr, uid, id, order, dt, context=None):
        total = 0
        weight = 0
        volume = 0
        if context is None:
            context = {}
        order_id = context.get('pos_order_id',False)
        #_logger.info('grid.get_price - order_id : %s'%order_id)
        if not order_id:
            res = super(delivery_grid, self).get_price(cr, uid, id, order, dt, context=context)
        else:
            for line in order.lines:
                if not line.product_id:
                    continue
                total += line.price_subtotal or 0.0
                weight += (line.product_id.weight or 0.0) * line.qty
                volume += (line.product_id.volume or 0.0) * line.qty
            res = self.get_price_from_picking(cr, uid, id, total,weight, volume, context=context)
        return res
        
delivery_grid()

class delivery_route_line(osv.osv):
    _name='delivery.route.line'
    _inherit='delivery.route.line'
    _columns = {
            'pos_order_id': fields.related('picking_id','pos_order_id',type='many2one',select=True,relation='pos.order',string='POS Order',readonly=True)
        }

    def action_delivered_do_line(self, cr, uid, line, context=None):
        super(delivery_route_line, self).action_delivered_do_line(cr, uid, line, context=context)
        if line.pos_order_id:
            self.pool.get('pos.order').write(cr,uid,line.pos_order_id.id,{'delivered':True},context=context)
        return True
        
    def action_cancel_do_line(self, cr, uid, line, context=None):
        super(delivery_route_line, self).action_cancel_do_line(cr, uid, line, context=context)
        if line.pos_order_id:
            self.pool.get('pos.order').write(cr,uid,line.pos_order_id.id,{'delivered':False},context=context)
        return True

delivery_route_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
