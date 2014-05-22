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
from tools.translate import _


class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    _columns = {
            'service_order_id': fields.many2one('service.order', string='Back Service Order', ondelete='set null'),
            'service_order_ids': fields.one2many('service.order','sale_order_id',string='Service Orders'),
            'sale_order_schedule_ids': fields.one2many('sale.order.schedule','sale_order_schedule_id',string='Service Schedules')
        }

sale_order()

class sale_order_schedule(osv.osv):
    _name = 'sale.order.schedule'
    _description = 'Sale Order Schedule'
    _columns = {
			'sale_order_schedule_id': fields.many2one('sale.order', string='Sale Order', ondelete='set null'),
            'serial_number_id': fields.many2one('stock.serial', string='Serial number', ondelete='set null'),
            'start_date':fields.date('Start Date')
        }
sale_order_schedule()

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    _columns = {
            'periodicity_id': fields.many2one('service.anual.time','Periodicity',required=False),
        }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        res = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag)
        
        if product:
            product = self.pool.get('product.product').browse(cr, uid, product, context=context)
            if product.periodicity and product.periodicity_id:
                res['value']['periodicity_id'] = product.periodicity_id.id
            
        return res
        
        
sale_order_line()
