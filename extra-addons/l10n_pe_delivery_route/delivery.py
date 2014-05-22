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
import time
import logging
_logger = logging.getLogger(__name__)

class delivery_route_line(osv.osv):
    _name = "delivery.route.line"
    _inherit = "delivery.route.line"
    _columns = {
            'district_id': fields.related('address_id','district_id',type='many2one',relation='res.country.district',select=True,string='Delivery District',readonly=True),
        }

delivery_route_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
