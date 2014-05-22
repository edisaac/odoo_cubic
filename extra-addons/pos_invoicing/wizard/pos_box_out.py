# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Teradata SAC - Cubic ERP (<http://cubicERP.com>).
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
from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import osv, fields
from tools.translate import _
import pos_box_entries

class pos_box_out(osv.osv_memory):
    _name = 'pos.box.out'
    _description = 'Pos Box Out'
    _inherit = 'pos.box.out'

    def get_out(self, cr, uid, ids, context=None):

        """
         Create the entries in the CashBox   .
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return :Return of operation of product
        """
        vals = {}
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        product_obj = self.pool.get('product.product')
        res_obj = self.pool.get('res.users')
        user = res_obj.browse(cr, uid, uid, context=context)
        curr_company = user.company_id.id
        for data in  self.read(cr, uid, ids, context=context):
            statement_ids = statement_obj.search(cr, uid, [('journal_id', '=', data['journal_id']), ('company_id', '=', curr_company), ('user_id', '=', uid), ('state', '=', 'open')], context=context)
            monday = (datetime.today() + relativedelta(weekday=0)).strftime('%Y-%m-%d')
            sunday = (datetime.today() + relativedelta(weekday=6)).strftime('%Y-%m-%d')
            done_statmt = statement_obj.search(cr, uid, [('date', '>=', monday+' 00:00:00'), ('date', '<=', sunday+' 23:59:59'), ('journal_id', '=', data['journal_id']), ('company_id', '=', curr_company), ('user_id', '=', uid)], context=context)
            stat_done = statement_obj.browse(cr, uid, done_statmt, context=context)
            am = 0.0
            product = product_obj.browse(cr, uid, data['product_id'], context=context)
            acc_id = product.property_account_expense or product.categ_id.property_account_expense_categ
            if not acc_id:
                raise osv.except_osv(_('Error !'), _('please check that account is set to %s')%(product.name))
            if not statement_ids:
                raise osv.except_osv(_('Error !'), _('You have to open at least one cashbox'))
            vals['statement_id'] = statement_ids[0]
            vals['journal_id'] = data['journal_id']
            vals['account_id'] = acc_id.id
            amount = data['amount'] or 0.0
            if data['amount'] > 0:
                amount = -data['amount']
            vals['amount'] = amount
            vals['name'] = "%s: %s " % (product.name, data['name'])
            #YT 12/04/2012 add shop_id
            vals['shop_id'] = user.shop_id.id
            statement_line_obj.create(cr, uid, vals, context=context)
        return {}

pos_box_out()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
