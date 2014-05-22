# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
# Copyright (c) 2011 Cubic ERP - Teradata SAC. (http://cubicerp.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import string

from osv import osv, fields
from tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def check_vat_pe (self,vat ):
        cstr = str (vat)
        salt=str (5432765432)
        n=0
        sum=0
        
        if not vat.isdigit:
            return False
        
        if (len (vat) <> 11):
            return  False

        while (n < 10):
            sum = sum + int (salt[n]) * int (cstr[n])
            n=n+1

        op1 = sum % 11
        op2 = 11 - op1

        verifiy_code = op2

        if ( op2 == 11 or op2 == 10):
            if ( op2 == 11 ):
                verifiy_code = 0
            else:
                verifiy_code = 9

        if ( verifiy_code == int (cstr[10]) ):
            return True                
        else:
            return False

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
