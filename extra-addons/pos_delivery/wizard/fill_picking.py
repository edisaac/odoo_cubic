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

from osv import osv, fields
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class route_fill_picking(osv.osv_memory):
    _name = 'delivery.route.fill.picking'
    _inherit = 'delivery.route.fill.picking'

    _columns = {
            'w_pos_order': fields.boolean("Find all pickings with pos order")
        }
    _defaults = {
            'w_pos_order': True
        }
    
    def get_picking_search_args(self,cr,uid,datas,context=None):
        srch = super(route_fill_picking, self).get_picking_search_args(cr, uid, datas, context=context)
        if datas.w_pos_order:
            srch += [('pos_order_id.id','>',0)]
        return srch

route_fill_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
