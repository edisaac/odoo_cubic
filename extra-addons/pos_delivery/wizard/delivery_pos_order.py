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

import time
from tools.translate import _

from osv import osv, fields

class make_delivery(osv.osv_memory):
    _name = "delivery.pos.order"
    _description = 'Make POS Delievery'

    _columns = {
        'carrier_id': fields.many2one('delivery.carrier','Carrier', required=True),
        'partner_id': fields.many2one('res.partner','Partner',readonly=True),
        'shipping_address_id': fields.many2one('res.partner.address','Address', readonly=True),
        'greeting': fields.char('Greeting', size=250, required=True),
        'greeting_date': fields.date('Greeting Date',required=True),
        'time_id': fields.many2one('delivery.time','Delivery Time', required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(make_delivery, self).default_get(cr, uid, fields, context=context)
        order_obj = self.pool.get('pos.order')
        for order in order_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if order.partner_id:
                res.update({'partner_id': order.partner_id.id})
                res.update({'shipping_address_id': order.shiping_address_id.id})
                if order.partner_id.property_delivery_carrier:
                    res.update({'carrier_id': order.partner_id.property_delivery_carrier.id})
             
        return res
    
    def view_init(self, cr , uid , fields, context=None):
         if context is None:
            context = {}
         order_obj = self.pool.get('pos.order')
         for order in order_obj.browse(cr, uid, context.get('active_ids', []), context=context):     
             if not order.state in ('draft'):
                 raise osv.except_osv(_('Order not in draft state !'), _('The order state have to be draft to add delivery lines.'))
         pass     

    def delivery_set(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        rec_ids = context and context.get('active_ids',[])
        order_obj = self.pool.get('pos.order')
        line_obj = self.pool.get('pos.order.line')
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')
        order_objs = order_obj.browse(cr, uid, rec_ids, context=context)
        for datas in self.browse(cr, uid, ids, context=context):    
            for order in order_objs:
                grid_id = carrier_obj.grid_get(cr, uid, [datas.carrier_id.id],order.shiping_address_id.id)
                if not grid_id:
                    raise osv.except_osv(_('No grid available !'), _('No grid matching for this carrier !'))

                if not order.state in ('draft'):
                    raise osv.except_osv(_('Order not in draft state !'), _('The order state have to be draft to add delivery lines.'))
                
                grid = grid_obj.browse(cr, uid, grid_id, context=context)

                line_obj.create(cr, uid, {
                    'order_id': order.id,
                    'name': grid.carrier_id.name,
                    'qty': 1,
                    'product_id': grid.carrier_id.product_id.id,
                    'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                })
                order_obj.write(cr, uid, [order.id], {
                    'greeting': datas.greeting,
                    'greeting_date': datas.greeting_date,
                    'time_id': datas.time_id.id,
                    'carrier_id': datas.carrier_id.id,
                    'delivered': False,
                })
    
        return {'type': 'ir.actions.act_window_close'}

make_delivery()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
