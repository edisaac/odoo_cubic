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


class service_order(osv.osv):
    _name = 'service.order'
    _description = 'Service Order'
    _columns = {
            'name': fields.char('Name', size=64, select=True, required=True),
            'sale_order_id': fields.many2one('sale.order', string='Sale Order', ondelete='set null'),
            'sale_order_ids': fields.one2many('sale.order','service_order_id',string='Back Sale Orders'),
            'analytic_id': fields.many2one('account.analytic.account','Analytic Account', ondelete='set null'),
            'picking_in_id': fields.many2one('stock.picking','Picking In', ondelete='set null'),
            'picking_out_id': fields.many2one('stock.picking','Picking Out', ondelete='set null'),
            'picking_ids': fields.one2many('stock.picking','service_order_id','Consmable Pickings'),
            'line_ids': fields.one2many('service.order.line','service_order_id','Service Order Lines'),
            'note': fields.text('Notes'),
            'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'State'),
        }
service_order()

class service_order_line(osv.osv):
    _name = 'service.order.line'
    _description = 'Service Order Line'
    _columns = {
            'name': fields.char('Name', size=64, select=True, required=True),
            'service_order_id': fields.many2one('service.order','Service Order', ondelete='cascade'),
            'move_id': fields.many2one('stock.move','Stock Move'),
            'workcenter_ids': fields.one2many('service.line.workcenter','service_line_id', string='Work Orders'),
            'serial_id': fields.many2one('stock.serial','Serial Number'),
            'description': fields.text('Description'),
            'part_ids': fields.one2many('service.line.part','service_line_id','Parts'),
            'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'State'),
        }
service_order_line()

class service_line_part(osv.osv):
    _name = 'service.line.part'
    _description = 'Service Order Line Part'
    _columns = {
            'service_line_id': fields.many2one('service.order.line','Service Order Line'),
            'serial_id': fields.many2one('stock.serial','Serial Number'),
            'gauge_start_id': fields.many2one('service.line.part.gauge','Gauge Start'),
            'gauge_end_id': fields.many2one('service.line.part.gauge','Gauge End')
        }
service_line_part()

class service_line_part_gauge(osv.osv):
    _name = 'service.line.part.gauge'
    _description = 'Service Order Line Part Gauge'
    _columns = {
            'date': fields.datetime('Date', required=True),
        #    'line_part_id': fields.many2one('service.line.part','Line part Id'),
            'cero': fields.float('Cero',digist=(2,1)),
            'cero_pattern': fields.float('Cero Pattern',digist=(2,1)),
            'cero_error': fields.float('Error',digist=(2,1)),
            'span': fields.float('SPAN',digist=(2,1)),
            'span_pattern': fields.float('SPAN Pattern',digist=(2,1)),
            'span_pattern_unit': fields.float('unit',digist=(2,1)),
            'span_error': fields.float('Error',digist=(2,1)),
            'time_rx_initial': fields.float('T. Rx Initial (seg)',digist=(2,1)),
            'time_stabilization': fields.float('T. Stabilization',digist=(2,1)),
            'oscillation': fields.float('Oscillation',digist=(2,1)),            
        }
service_line_part_gauge()

class service_line_workcenter(osv.osv):
    _name = 'service.line.workcenter'
    _inherit = ['mrp.production.workcenter.line']
    _description = 'Service Order Line Workcenter'
    _columns = {
            'production_id': fields.many2one('mrp.production','Production Order',required=False),
            'service_line_id': fields.many2one('service.order.line','Service Order Line', required=True),
        }
service_line_workcenter()

class service_anual_time(osv.osv):
    _name = 'service.anual.time'
    _description = 'Service anual Time'
    _columns = {
            'name': fields.char('Name', size=64, select=True, required=True),
            'periodicity': fields.integer('Periodicity'),
        }
service_anual_time()
