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
import datetime
import logging
from tools.translate import _
_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
    _name = "pos.order"
    _inherit = "pos.order"
    
    def _get_pos_order_from_route_line(self, cr, uid, ids, context=None):
        res = {}
        for line in self.pool.get('delivery.route.line').browse(cr,uid,ids,context=context):
            if line.pos_order_id:
                res[line.pos_order_id.id] = True
        return res.keys()
    
    def _route_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for i in ids:
            res[i] = False
        line_obj = self.pool.get('delivery.route.line')
        line_ids = line_obj.search(cr,uid,[('pos_order_id','in',ids)],context=context)
        for line in line_obj.browse(cr,uid,line_ids,context=context):
            res[line.pos_order_id.id] = line.state
        return res
    
    _columns = {
        'shiping_address_id': fields.many2one("res.partner.address","Delivery Address", domain="[('partner_id','=',partner_id)]",
                                            readonly=True, states={'draft':[('readonly', False)]}),
        'picking_print': fields.boolean('Print Picking',readonly=True),
        'carrier_id': fields.many2one("delivery.carrier", "Delivery Carrier", help="The carrier reponsible for shipping"),
        'greeting': fields.char('Greeting',size=250),
        'greeting_print': fields.boolean('Print Greeting',readonly=True),
        'greeting_date': fields.date('Delivery Date'),
        'time_id': fields.many2one('delivery.time','Delivery Time'),

        'route_state' : fields.function(_route_state,type="char",method=True,string="Route State",readonly=True,
                                            store={'delivery.route.line':(_get_pos_order_from_route_line,['state'],10)}),
        'delivered': fields.boolean('Delivered', readonly=True),

        'visit_date' : fields.related('picking_id','route_line_id','visit_date',string='Visit Date',type='datetime',readonly=True),
        'visit_note' : fields.related('picking_id','route_line_id','visit_note',string='Visit Note',type='char',readonly=True),

    }
    
    _defaults = {
        'delivered': True,
        'greeting_print': False,
        'picking_print': False,
    }

    def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
        if not part:
            return {'value': {}}
        res = super(pos_order,self).onchange_partner_id(cr, uid, ids, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery'])
        res['value'].update({'shiping_address_id':addr['delivery']})
        return res
        
    def unlink(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.state not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), 
                        _('Cannot delete POS Order(s) which are already invoiced, posted or paid !'))
            if order.picking_id and (order.picking_id.state=='cancel'):
                raise osv.except_osv(_('Invalid action !'), 
                        _('Cannot delete POS Order(s) which are picking in other state than cancel !'))
            if order.picking_id and order.picking_id.route_line_id:
                self.pool.get('delivery.route.line').unlink(cr,uid,[order.picking_id.route_line_id.id],context=context)
        return super(pos_order, self).unlink(cr, uid, ids, context=context)

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')

        for order in self.browse(cr, uid, ids, context=context):
            if not order.state=='draft':
                continue
            addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
            date_expected = time.strftime('%Y-%m-%d %H:%M:%S')
            time_id_start = " 00:00:00"
            res_picking = {
                'origin': order.name,
                'address_id': addr.get('delivery',False),
                'type': 'out',
                'company_id': order.company_id.id,
                'move_type': 'direct',
                'note': order.note or "",
                'invoice_state': 'none',
                'auto_picking': True,
            }
            #YT 3/5/2012 Add some features
            res_picking.update({'delivered':order.delivered})
            if order.carrier_id:
                res_picking.update({'carrier_id':order.carrier_id.id})
            if order.shop_id and order.shop_id.warehouse_id and order.shop_id.warehouse_id.stock_journal_id:
                res_picking.update({'stock_journal_id':order.shop_id.warehouse_id.stock_journal_id.id})
            if order.time_id:
                time_id_start = " %s:%s:00"%(order.time_id.start_hour.zfill(2),order.time_id.start_minute.zfill(2))
                res_picking.update({'time_id':order.time_id.id})
            if order.greeting_date:
                date_expected = str(order.greeting_date) + time_id_start
                res_picking.update({'delivery_date':order.greeting_date})
                
            picking_id = picking_obj.create(cr, uid, res_picking, context=context)
            self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            location_id = order.shop_id.warehouse_id.lot_stock_id.id
            output_id = order.shop_id.warehouse_id.lot_output_id.id

            for line in order.lines:
                if line.product_id and line.product_id.type == 'service':
                    continue
                if line.qty < 0:
                    location_id, output_id = output_id, location_id

                move_obj.create(cr, uid, {
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.qty),
                    'product_qty': abs(line.qty),
                    'tracking_id': False,
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': output_id,
                    'date_expected': date_expected,
                }, context=context)
                if line.qty < 0:
                    location_id, output_id = output_id, location_id
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            #YT 4/5/2012 Support for process the picking
            if order.delivered:
                picking_obj.force_assign(cr, uid, [picking_id], context)
                
        return True


pos_order()

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'birthday':fields.date('Birthday'),
        'event_ids': fields.one2many('res.partner.events','partner_event_id','Important Dates'),
        }
res_partner()

class delivery_partner_events(osv.osv):
    _name = "res.partner.events"

    _columns = {
        'date':fields.date('Date'),
        'description': fields.char('Description', size=120, select=True, required=True),
        'partner_event_id': fields.many2one('res.partner','Partner Id'),
        }
delivery_partner_events()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
