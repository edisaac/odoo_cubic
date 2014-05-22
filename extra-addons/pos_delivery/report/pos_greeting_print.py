# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Teradata SAc - Cubic ERP (<http://cubicerp.com>).
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
from report import report_sxw
import netsvc

class pos_greeting_print(report_sxw.rml_parse):
    _name = 'report.pos.greeting.print'
    _cr = None
    _uid = None
    def __init__(self, cr, uid, name, context):
        super(pos_greeting_print, self).__init__(cr, uid, name, context)
        self._cr = cr
        self._uid = uid
        self.localcontext.update({
            'time': time,
            'day': self.day,
            'month': self.month,
            'year': self.year,
        })
    
    def day(self, date): return self.pool.get('ir.translation').date_part(date, 'day', format='number' ,lang='pe')
    
    def month(self, date): return self.pool.get('ir.translation').date_part(date, 'month', format='text' ,lang='pe')
    
    def year(self, date): return self.pool.get('ir.translation').date_part(date, 'year', format='number' ,lang='pe')
    
report_sxw.report_sxw(
    'report.pos.greeting.print',
    'pos.order',
    'addons/pos_delivery/report/pos_greeting_print.rml',
    parser=pos_greeting_print,header=False
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
