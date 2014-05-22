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

import tools
from osv import fields,osv

class report_cash_register_detail(osv.osv):
    _name = "report.cash.register.detail"
    _description = "Point of Sale Cash Register Detailed Analysis"
    _auto = False
    _columns = {
        'date': fields.date('Create Date', readonly=True),
        'year': fields.char('Year', size=4),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'),
            ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'),
            ('10','October'), ('11','November'), ('12','December')], 'Month',readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'user_id':fields.many2one('res.users', 'User', readonly=True),
        'state': fields.selection([('draft', 'Quotation'),('open','Open'),('confirm', 'Confirmed')],'State'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'balance_start': fields.float('Opening Balance'),
        'balance_end_real': fields.float('Closing Balance'),
        'name': fields.char('Register', size=64),
        'account_id': fields.many2one('account.account', 'Account'),
        'shop_id': fields.many2one('sale.shop', 'Shop'),
        'pos_id': fields.many2one('pos.order', 'POS Order'),
        'amount': fields.float('Amount'),
    }
    _order = 'date desc, name desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_cash_register_detail')
        cr.execute("""
            create or replace view report_cash_register_detail as (
                select
                    min(sl.id) as id,
                    to_date(to_char(s.create_date, 'dd-MM-YYYY'),'dd-MM-YYYY') as date,
                    s.user_id as user_id,
                    s.journal_id as journal_id,
                    s.state as state,
                    s.balance_start as balance_start,
                    s.balance_end_real as balance_end_real,
                    to_char(s.create_date, 'YYYY') as year,
                    to_char(s.create_date, 'MM') as month,
                    to_char(s.create_date, 'YYYY-MM-DD') as day,
                    s.name as name,
                    sl.account_id as account_id,
                    sl.shop_id as shop_id,
                    sum(sl.amount) as amount,
                    sl.pos_statement_id as pos_id
                from account_bank_statement as s, 
                     account_bank_statement_line as sl
               where s.id = sl.statement_id
                group by
                        s.user_id,s.journal_id, s.balance_start, s.balance_end_real,s.state,s.name,sl.account_id,sl.shop_id,sl.pos_statement_id,
                        to_char(s.create_date, 'dd-MM-YYYY'),
                        to_char(s.create_date, 'YYYY'),
                        to_char(s.create_date, 'MM'),
                        to_char(s.create_date, 'YYYY-MM-DD'))""")

report_cash_register_detail()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
