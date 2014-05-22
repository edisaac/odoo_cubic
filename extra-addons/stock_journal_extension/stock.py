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
import netsvc
from osv.orm import browse_record, browse_null
import time

class stock_journal(osv.osv):
    _name = "stock.journal"
    _inherit = 'stock.journal'
    _columns = {
            'sequence_id': fields.many2one('ir.sequence','Sequence'),
            'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
            'carrier_id':fields.many2one("delivery.carrier","Carrier"),
            'user_ids': fields.many2many('res.users','stock_journal_users','journal_id','user_id',string='Users Access',help="User Access use empty for full access"),
        }
stock_journal()

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = 'stock.picking'
    
    def create(self, cr, user, vals, context=None):
        #YT 4/5/2012
        #if ('name' not in vals) or (vals.get('name')=='/'):
        #    seq_obj_name =  'stock.picking.' + vals['type']
        #    vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        return new_id

    def action_assign_wkf(self, cr, uid, ids, context=None):
        
        for picking in self.browse(cr, uid, ids, context=context):
            res = {}
            if picking.name or picking.name == '/':
                if picking.type == 'in':
                    res['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.' + picking.type)
                else:
                    if picking.stock_journal_id and picking.stock_journal_id.sequence_id:
                        res['name'] = self.pool.get('ir.sequence').get_id(cr, uid, picking.stock_journal_id.sequence_id.id)
                    else:
                        res['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.' + picking.type)
            if res:
                self.write(cr,uid,[picking.id],res,context=context)
                
        return super(stock_picking, self).action_assign_wkf(cr, uid, ids, context=context)
        
    def onchange_journal(self, cr, uid, ids, journal_id, type='out', context=None):
        if context is None: context={}
        if not journal_id: return {}
        res = {}
        #netsvc.Logger().notifyChannel("onchange_journal", netsvc.LOG_INFO, "journal_id: %s, type:%s, context:%s" %(journal_id,type,context))
        journal = self.pool.get('stock.journal').browse(cr, uid, journal_id)
        #netsvc.Logger().notifyChannel("onchange_journal", netsvc.LOG_INFO, "journal:%s" %(journal))
        if journal.warehouse_id:
            if type=='out':
                context['location_id'] = journal.warehouse_id.lot_stock_id.id
                context['location_dest_id'] = journal.warehouse_id.lot_output_id.id
            elif type=='in':
                context['location_dest_id'] = journal.warehouse_id.lot_stock_id.id
        if journal.carrier_id:
            res['value'] = {'carrier_id':journal.carrier_id.id}
        return res
        
    def _default_location_destination(self, cr, uid, context=None):
        res = super(stock_picking, self)._default_location_destination(cr, uid, context=context)
        if not res: 
            res = context.get('location_des_id', False)
        return res

    def _default_location_source(self, cr, uid, context=None):
        res = super(stock_picking, self)._default_location_source(cr, uid, context=context)
        if not res: 
            res = context.get('location_id', False)
        return res
        
    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of pickings.
        Picking will only be merged if:
        * Pickings are in draft, confirmed 
        * Pickings belong to the same partner and type
        * Pickings are have same stock locations, same stock journal
        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new picking id {neworder_id: old_ids,...}

        """
        wf_service = netsvc.LocalService("workflow")
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('purchase_id', 'sale_id','pos_order', 'prodlot_id', 'tracking_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

    # compute what the new pickings should contain

        new_pickings = {}

        for picking in [order for order in self.browse(cr, uid, ids, context=context) if order.state in ('draft','confirmed')]:
            picking_key = make_key(picking, ('address_id', 'stock_journal_id','type','move_type','state','carrier_id','backorder_id','purchase_id', 'sale_id','pos_order','company_id'))
            new_picking = new_pickings.setdefault(picking_key, ({}, []))
            new_picking[1].append(picking.id)
            picking_infos = new_picking[0]
            if not picking_infos:
                picking_infos.update({
                    'origin': picking.origin,
                    'date': time.strftime('%Y-%m-%d'),
                    'address_id': picking.address_id and picking.address_id.id or False,
                    'backorder_id': picking.backorder_id and picking.backorder_id.id or False,
                    'move_type': picking.move_type,
                    'type': picking.type,
                    'state': picking.state,
                    'note': '%s' % (picking.note or '',),
                    'carrier_id' : picking.carrier_id and picking.carrier_id.id or False,
                    'move_lines': {},
                })
                if self.pool.get('stock.picking').fields_get(cr,uid,['purchase_id'],context=context) and picking.purchase_id:
                    picking_infos.update({'purchase_id':picking.purchase_id.id})
                if self.pool.get('stock.picking').fields_get(cr,uid,['sale_id'],context=context) and picking.sale_id:
                    picking_infos.update({'sale_id':picking.sale_id.id})
                if self.pool.get('stock.picking').fields_get(cr,uid,['pos_order'],context=context) and picking.pos_order:
                    picking_infos.update({'pos_order':picking.pos_order.id})
                
            else:
                if picking.note:
                    picking_infos['note'] = (picking_infos['note'] or '') + ('\n%s' % (picking.note,))
                if picking.origin:
                    picking_infos['origin'] = (picking_infos['origin'] or '') + ' ' + picking.origin

            for move_line in picking.move_lines:
                line_key = make_key(move_line, ('address_id','date_expected','prodlot_id','move_dest_id','location_id','location_dest_id','name','product_id','auto_validate','company_id','priority','state','tracking_id','product_packaging'))
                o_line = picking_infos['move_lines'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += move_line.product_qty * move_line.product_uom.factor / o_line['uom_factor']
                    o_line['product_uos_qty'] += move_line.product_uos_qty * move_line.product_uos.factor / o_line['uos_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom','product_uos_qty','product_uos'):
                        field_val = getattr(move_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = move_line.product_uom and move_line.product_uom.factor or 1.0
                    o_line['uos_factor'] = move_line.product_uos and move_line.product_uos.factor or 1.0
                    if self.pool.get('stock.move').fields_get(cr,uid,['purchase_line_id'],context=context) and move_line.purchase_line_id:
                        o_line.update({'purchase_line_id':move_line.purchase_line_id.id})
                    if self.pool.get('stock.move').fields_get(cr,uid,['sale_line_id'],context=context) and move_line.sale_line_id:
                        o_line.update({'sale_line_id':move_line.sale_line_id.id})
                    if self.pool.get('stock.move').fields_get(cr,uid,['production_id'],context=context) and move_line.production_id:
                        o_line.update({'production_id':move_line.production_id.id})

                if move_line.origin:
                    o_line['origin'] = o_line.get('origin','') + ' ' + move_line.origin
                if move_line.note:
                    o_line['note'] = o_line.get('note','') + ' ' + move_line.note

        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_pickings.iteritems():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['move_lines'].iteritems():
                del value['uom_factor']
                del value['uos_factor']
                value.update(dict(key))
            order_data['move_lines'] = [(0, 0, value) for value in order_data['move_lines'].itervalues()]

            # create the new picking
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'stock.picking', old_id, neworder_id, cr)
                wf_service.trg_validate(uid, 'stock.picking', old_id, 'button_cancel', cr)
        return orders_info


        
stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _name = "stock.move"

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the moves and if all moves are cancelled it cancels the picking.
        @return: True
        """
        if not len(ids):
            return True
        if context is None:
            context = {}
        pickings = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('confirmed', 'waiting', 'assigned', 'draft'):
                if move.picking_id:
                    pickings[move.picking_id.id] = True
            if move.move_dest_id and move.move_dest_id.state == 'waiting':
                #YT 30/11/2011
                move_dest_ids = [move.move_dest_id.id]
                if self.pool.get('stock.move').fields_get(cr,uid,['merge_move_dest'],context=context):
                    move_dest_ids += self.pool.get('stock.move').search(cr, uid, [('merge_move_dest','=',move.move_dest_id.id)])
                self.write(cr, uid, move_dest_ids, {'state': 'confirmed'})
                #self.write(cr, uid, [move.move_dest_id.id], {'state': 'assigned'})
                
                if context.get('call_unlink',False) and move.move_dest_id.picking_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
        self.write(cr, uid, ids, {'state': 'cancel', 'move_dest_id': False})
        if not context.get('call_unlink',False):
            for pick in self.pool.get('stock.picking').browse(cr, uid, pickings.keys()):
                if all(move.state == 'cancel' for move in pick.move_lines):
                    self.pool.get('stock.picking').write(cr, uid, [pick.id], {'state': 'cancel'})

        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)
        return True

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                
                #YT 1/12/2011
                move_dest_ids = [move.move_dest_id.id]
                if self.pool.get('stock.move').fields_get(cr,uid,['merge_move_dest'],context=context):
                    move_dest_ids += self.pool.get('stock.move').search(cr, uid, [('merge_move_dest','=',move.move_dest_id.id)])                
                for move_dest_id in move_dest_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move_dest_id)]})
                    #cr.execute('insert into stock_move_history_ids (parent_id,child_id) values (%s,%s)', (move.id, move.move_dest_id.id))
                if move.move_dest_id.state in ('waiting', 'confirmed'):
                    if move.prodlot_id.id and move.product_id.id == move.move_dest_id.product_id.id:
                        self.write(cr, uid, move_dest_ids, {'prodlot_id':move.prodlot_id.id})
                    self.force_assign(cr, uid, move_dest_ids, context=context)
                    for move_dest_id in self.pool.get('stock.move').browse(cr,uid,move_dest_ids,context=context):
                        if move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move_dest_id.picking_id.id, cr)
                    if move.move_dest_id.auto_validate:
                        self.action_done(cr, uid, move_dest_ids, context=context)
                #self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                ##cr.execute('insert into stock_move_history_ids (parent_id,child_id) values (%s,%s)', (move.id, move.move_dest_id.id))
                #if move.move_dest_id.state in ('waiting', 'confirmed'):
                #    self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                #    if move.move_dest_id.picking_id:
                #        wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                #    if move.move_dest_id.auto_validate:
                #        self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed','done','assigned'):
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        for id in move_ids:
             wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True

    
stock_move()
