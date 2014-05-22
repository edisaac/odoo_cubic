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

class account_journal(osv.osv):
    _name = 'account.journal'
    _inherit = 'account.journal'
    _columns = {
            'int_trade': fields.boolean('International Trade', help="Purchase or Sale Journal, used to international trade"),
            'customs': fields.boolean('Customs Journal', help="Purchase Journal, used to register customs declarations as DUA"),
        }
        
account_journal()

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    _name = "account.invoice"
    _columns = {
            'int_trade': fields.related('journal_id','int_trade',string='International Trade',type='boolean',store=True,readonly=True),
            'customs': fields.related('journal_id','customs',string='Customs Invoice',type='boolean',store=True,readonly=True),
            'customs_invoice_id': fields.many2one('account.invoice',string='Customs Declaration'),
            'customs_other_id': fields.many2one('account.invoice',string='Customs Purchase Liquidation'),
            'freight_id': fields.many2one('account.invoice',string='International Freight'),
            'insurance_id': fields.many2one('account.invoice',string='Cargo Insurance'),
            'other_invoice_ids': fields.many2many('account.invoice','account_trade_other_invoice','invoice_id','other_invoice_id',string="Expenses, penaltys and others")
        }
    
account_invoice()

class account_invoice_line(osv.osv):
    
    _inherit = 'account.invoice.line'
    _name = "account.invoice.line"
    _columns = {
            'prorated_price': fields.float('Prorated Unit Price'),
            'prorated_percent': fields.float('Prorated Percent(%)'),
        }
    
account_invoice_line()
