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
import logging
from tools.translate import _

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'journal_users': fields.many2many('res.users', 'pos_journal_users', 'journal_id', 'user_id', 'Users'),
        'currency_rate': fields.related('currency','rate',type='float'),
    }

account_journal()

class account_cash_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def _user_allow(self, cr, uid, statement_id, context=None):
        statement = self.browse(cr, uid, statement_id, context=context)
        if (not statement.journal_id.journal_users) and uid == 1: return True
        for user in statement.journal_id.journal_users:
            if uid == user.id:
                return True
        return False
        
    #YT 31/03/2012 Add support for multipes cash journals
    # def create(... se encuentra como parche no funciona sobrescrito por el super()
            
    #YT 27/03/2012 el start y end deben estar al revez segun el create and support multile journals
    def _get_cash_open_close_box_lines(self, cr, uid, journal_id, context=None):
        res = {}
        start_l = []
        end_l = []
        starting_details = self._get_cash_open_box_lines(cr, uid, journal_id, context=context)
        ending_details = self._get_default_cash_close_box_lines(cr, uid, context)
        for start in starting_details:
            start_l.append((0, 0, start))
        for end in ending_details:
            end_l.append((0, 0, end))
        res['start'] = end_l
        res['end'] = start_l
        return res
    
    def _get_cash_open_box_lines(self, cr, uid, journal_id, context=None):
        res = []
        curr = [0.10, 0.20, 0.50 , 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
        for rs in curr:
            dct = {
                'pieces': rs,
                'number': 0
            }
            res.append(dct)
        # YT 31/03/2012 adds support for multiple journals
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('id', '=', journal_id),('type', '=', 'cash'),('journal_user','=',1),('journal_users','in',(uid))], context=context)
        if journal_ids:
            cr.execute("select id from account_bank_statement where journal_id=%s and state='confirm' order by name desc limit 1"%(journal_id))
            results = map(lambda x1: x1[0], cr.fetchall())
            #results = self.search(cr, uid, [('journal_id', 'in', journal_ids),('state', '=', 'confirm')], context={})
            if results:
                cash_st = self.browse(cr, uid, results, context=context)[0]
                for cash_line in cash_st.ending_details_ids:
                    #logging.getLogger('server').info('cash_line.pieces:%s - cash_line.number: %s'%(cash_line.pieces,cash_line.number))
                    for r in res:
                        #logging.getLogger('server').info('r:%s'%(r))
                        if cash_line.pieces == r['pieces']:
                            r['number'] = cash_line.number
        return res

    def _get_default_cash_close_box_lines(self, cr, uid, context=None):
        res = []
        curr = [0.10, 0.20, 0.50 , 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
        for rs in curr:
            dct = {
                'pieces': rs,
                'number': 0
            }
            res.append(dct)
        return res

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        st = self.browse(cr, uid, st_id, context=context)
        #YT 03/04/2012 Fix it
        balance_end = st.balance_start + st.total_entry_encoding
        balance_end_real = st.balance_end_real or balance_end
        #if ((abs((balance_end or 0.0) - balance_end_real) > 0.0001) or (abs((balance_end or 0.0) - st.balance_end_cash) > 0.0001)):
        if (abs((balance_end or 0.0) - st.balance_end_cash) > 0.0001):
            raise osv.except_osv(_('Error !'),
                    _('The statement balance is incorrect !\nThe expected balance (%.2f) is different than the computed one. (%.2f) (%.2f)') % (st.balance_end_cash, balance_end, balance_end_real))
        return True

account_cash_statement()

class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop'),
    }

account_bank_statement_line()
