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
import netsvc
import logging
_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
    _name = "pos.order"
    _inherit = "pos.order"
    
    _columns = {
        'shipping_district_id' : fields.related('shiping_address_id','district_id',string='Delivery District',type='many2one',relation='res.country.district',readonly=True,store=True),

    }
    
        
pos_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
