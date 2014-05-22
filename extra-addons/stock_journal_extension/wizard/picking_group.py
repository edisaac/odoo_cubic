# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _

class picking_group(osv.osv_memory):
    _name = "stock.picking.group"
    _description = "Stock Picking Merge"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        if context is None:
            context={}
        res = super(picking_group, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if context.get('active_model','') == 'stock.picking' and len(context['active_ids']) < 2:
            raise osv.except_osv(_('Warning'),
            _('Please select multiple pickings to merge in the list view.'))
        return res
    def merge_pickings(self, cr, uid, ids, context=None):
        """
             To merge similar type of picking.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: picking view

        """
        picking_obj = self.pool.get('stock.picking')
        proc_obj = self.pool.get('procurement.order')
        mod_obj =self.pool.get('ir.model.data')
        if context is None: context = {}
        result = mod_obj._get_id(cr, uid, 'stock', 'view_picking_in_search')
        id = mod_obj.read(cr, uid, result, ['res_id'])

        allpickings = picking_obj.do_merge(cr, uid, context.get('active_ids',[]), context)

        #for new_order in allpickings:
        #    proc_ids = proc_obj.search(cr, uid, [('move_id', 'in', allpickings[new_order])], context=context)
        #    for proc in proc_obj.browse(cr, uid, proc_ids, context=context):
        #        if proc.move_id:
        #            proc_obj.write(cr, uid, [proc.id], {'move_id': new_order}, context)

        return {
            'domain': "[('id','in', [" + ','.join(map(str, allpickings.keys())) + "])]",
            'name': 'Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': id['res_id']
        }

picking_group()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
