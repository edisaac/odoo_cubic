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

class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"
    
    def grid_get(self, cr, uid, ids, contact_id, context=None):
        contact = self.pool.get('res.partner.address').browse(cr, uid, contact_id, context=context)
        for carrier in self.browse(cr, uid, ids, context=context):
            for grid in carrier.grids_id:
                get_id = lambda x: x.id
                country_ids = map(get_id, grid.country_ids)
                state_ids = map(get_id, grid.state_ids)
                province_ids = map(get_id, grid.province_ids)
                district_ids = map(get_id, grid.district_ids)
                if country_ids and not contact.country_id.id in country_ids:
                    continue
                if state_ids and not contact.state_id.id in state_ids:
                    continue
                if province_ids and not contact.province_id.id in province_ids:
                    continue
                if district_ids and not contact.district_id.id in district_ids:
                    continue
                if grid.zip_from and (contact.zip or '')< grid.zip_from:
                    continue
                if grid.zip_to and (contact.zip or '')> grid.zip_to:
                    continue
                return grid.id
        return False
    
delivery_carrier()

class delivery_grid(osv.osv):
    _name = "delivery.grid"
    _inherit = "delivery.grid"
    _columns = {
            'province_ids': fields.many2many('res.country.province','delivery_grid_province_rel','grid_id','province_id','Provinces'),
            'district_ids': fields.many2many('res.country.district','delivery_grid_district_rel','grid_id','district_id','Districts'),
        }

delivery_grid()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
