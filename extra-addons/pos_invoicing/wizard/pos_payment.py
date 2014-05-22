# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Teradata SAC - Cubic ERP (<http://cubicerp.com>).
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
import pos_box_entries
import netsvc
import logging

_logger = logging.getLogger(__name__)

class pos_make_payment(osv.osv_memory):
    _name = 'pos.make.payment'
    _inherit = 'pos.make.payment'
    
    def check(self, cr, uid, ids, context=None):
        """Check the order:
        if the order is not paid: continue payment,
        if the order is paid print ticket.
        """
        context = context or {}
        order_obj = self.pool.get('pos.order')
        obj_partner = self.pool.get('res.partner')
        active_id = context and context.get('active_id', False)

        order = order_obj.browse(cr, uid, active_id, context=context)
        amount = order.amount_total - order.amount_paid
        data = self.read(cr, uid, ids, context=context)[0]
        # this is probably a problem of osv_memory as it's not compatible with normal OSV's
        #data['journal'] = data['journal'][0]

        if amount != 0.0:
            order_obj.add_payment(cr, uid, active_id, data, context=context)

        if order_obj.test_paid(cr, uid, [active_id]):
            # YT 17/04/2012 change the number of POS Order
            data_upd = {}
            sale_journal_id = order.shop_id.sale_journal_id.id
            sequence_id = order.shop_id.sale_journal_id.sequence_id.id
            if context.get('invoice', 0) and order.shop_id.invoice_journal_id:
                sale_journal_id = order.shop_id.invoice_journal_id.id
                sequence_id = order.shop_id.invoice_journal_id.sequence_id.id
                data_upd.update({'sale_journal':sale_journal_id})
            if not order.name or order.name == '/':
                curr_seq = self.pool.get('ir.sequence').next_by_id(cr, uid, sequence_id)
                data_upd.update({'name':curr_seq})
            #_logger.info("data_upd: %r", data_upd)
            if data_upd:
                order_obj.write(cr, uid, [active_id], data_upd, context=context)
            #YT 8/5/2012 write SO origin
            order = order_obj.browse(cr, uid, active_id, context=context)
            if order.picking_id:
                self.pool.get('stock.picking').write(cr,uid,[order.picking_id.id],{'origin':order.name},context=context)
            
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'pos.order', active_id, 'paid', cr)
            return self.print_report(cr, uid, ids, context=context)

        return self.launch_payment(cr, uid, ids, context=context)

    def print_report(self, cr, uid, ids, context=None):
        active_id = context.get('active_id', [])
        datas = {'ids' : [active_id]}
        # YT 17/04/2012 add support for multiple reports
        report_name = context.get('report_name', 'pos.receipt')
        self.pool.get('pos.order').write(cr, uid, [active_id], {'report_name':report_name}, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }
    # YT 17/04/2012 add support for journal_users in get_journal
    def _default_journal(self, cr, uid, context=None):
        res = pos_box_entries.get_journal(self, cr, uid, context=context)
        return len(res)>1 and res[1][0] or False

pos_make_payment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
