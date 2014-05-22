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

class account_printer(osv.osv):
    _name = "account.printer"
    _description = "Printer defined to obtain the serial number for fiscal purposes"
    _columns = {
        'name': fields.char('Serial Number', size=64, required=True),
        'model': fields.char('Model', size=64),
        'active': fields.boolean('Active'),
    }
account_printer()

class account_journal(osv.osv):
    _name = "account.journal"
    _inherit = "account.journal"
    
    _columns = {
        'printer_id': fields.many2one('account.printer', string="POS Printer", ondelete="set null"),
    }
account_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
