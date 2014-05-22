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

class sale_printer(osv.osv):
    _name = "sale.printer"
    _description = "Printer defined to obtain the serial number for fiscal purposes"
    _columns = {
        'name': fields.char('Serial Number',size=64, required=True),
        'model': fields.char('Model',size=64),
        'active': fields.boolean('Active'),
        'shop_ids': fields.one2many('sale.shop', 'printer_id', string='Account Journals'),
    }
    _defaults = {
		'active': True,
    }
sale_printer()

class res_users(osv.osv):
	_name = "res.users"
	_inherit = "res.users"
	
	_columns = {
		'shop_id': fields.many2one('sale.shop', string='Sale Shop'),
	}
res_users()

class sale_shop(osv.osv):
    _name = "sale.shop"
    _inherit = "sale.shop"

    def _sale_journal_get(self, cr, uid, context=None):
        """ To get  sale journal for this order
        @return: journal  """
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', 'sale')], limit=1)
        return res and res[0] or False

    _columns = {
            'user_ids': fields.one2many('res.users','shop_id',string="POS User Access"),
            'sale_journal_id': fields.many2one('account.journal', string='POS Sale Journal', domain=[('type', '=', 'sale')], required=True,
				    help="The sequence of this journal must be unique by each point (computer and printer). This is useful according some tributary laws"),
            'invoice_journal_id': fields.many2one('account.journal', string='POS Invoice Journal', domain=[('type', '=', 'sale')],
				    help="Optional if this shop are permited to print invoices with VAT number. The sequence of this journal must be unique by each point (computer and printer). This is useful according some tributary laws"),
            'printer_id': fields.many2one('sale.printer', string="Printer", ondelete="set null"),
            'printer_serial': fields.related('printer_id', 'name', string='Printer Serial', readonly=True),
	    'invoice_number_next': fields.related('invoice_journal_id','sequence_id','number_next', string='Invoice Next Number', type='integer', readonly=True),
	    'invoice_number_prefix': fields.related('invoice_journal_id','sequence_id','prefix', string='Invoice Sequence Prefix', type='char', readonly=True),
	    'invoice_number_increment': fields.related('invoice_journal_id','sequence_id','number_increment', string='Invoice Increment Number', type='integer', readonly=True),
	    'invoice_number_padding': fields.related('invoice_journal_id','sequence_id','padding', string='Invoice Number Padding', type='integer', readonly=True),
	    'sale_number_next': fields.related('sale_journal_id','sequence_id','number_next', string='Sale Next Number', type='integer', readonly=True),
	    'sale_number_prefix': fields.related('sale_journal_id','sequence_id','prefix', string='Sale Sequence Prefix', type='char', readonly=True),
	    'sale_number_increment': fields.related('sale_journal_id','sequence_id','number_increment', string='Sale Increment Number', type='integer', readonly=True),
	    'sale_number_padding': fields.related('sale_journal_id','sequence_id','padding', string='sale Number Padding', type='integer', readonly=True),
	    'online': fields.boolean('Online',help="Allow to open multiple chashboxs at the same time, using the POS Backend"),
        }
    _defaults = {
            'sale_journal_id': _sale_journal_get,
            'online':0,
        }

sale_shop()
