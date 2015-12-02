# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Cubic ERP SAC (<http://cubicerp.com>).
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

from openerp import api, models

class report_picking_cost(models.AbstractModel):
    _name = 'report.stock_landed_costs.report_picking_cost'
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock_landed_costs.report_picking_cost')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(self._ids),
            'get_cost_names': self.get_cost_names,
            'get_cost_lines': self.get_cost_lines,
            'get_cost_total': self.get_cost_total,
        }
        return report_obj.render('stock_landed_costs.report_picking_cost', docargs)
    
    def get_cost_names(self, landed_costs_ids):
        res = ""
        for cost in landed_costs_ids:
            res += cost.name + " / "
        return res and res [:-3] or ""
    
    def get_cost_total(self, landed_costs_ids):
        res = 0.0
        for cost in landed_costs_ids:
            res += cost.amount_total 
        return res
    
    def get_cost_lines(self, landed_costs_ids):
        res = []
        for cost in landed_costs_ids:
            for line in cost.cost_lines:
                res.append(line)
        return res