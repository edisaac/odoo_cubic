# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import fields as fields2
from openerp import models, api

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res['asset_id'] = x.get('asset_id', False)
        return res


class account_invoice_line(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    asset_id = fields2.Many2one('account.asset.asset', 'Asset')

    @api.model
    def move_line_get_item(self, line):
        res = super(account_invoice_line, self).move_line_get_item(line)
        if line.asset_id:
            res['asset_id'] = line.asset_id.id
        return res

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.account_id = self.asset_id.account_asset_id.id or self.asset_id.category_id.account_asset_id.id
            self.account_analytic_id = self.asset_id.account_analytic_id.id or self.asset_id.category_id.account_analytic_id.id


class account_entries_report(osv.osv):
    _name = "account.entries.report"
    _inherit = "account.entries.report"

    _columns = {
        'asset_id': fields.many2one('account.asset.asset', 'Asset', readonly=True),
        'parent_asset_id': fields.many2one('account.asset.asset', 'Asset Parent', readonly=True),
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category', readonly=True),
        'asset_parent_category_id': fields.many2one('account.asset.category', 'Asset Parent Category', readonly=True),
    }

    def _get_select(self):
        res = super(account_entries_report, self)._get_select()
        return """%s,
         l.asset_id as asset_id,
         aasset.parent_id as parent_asset_id,
         aasset.category_id as asset_category_id,
         assetcategory.parent_id as asset_parent_category_id
        """%(res)

    def _get_from(self):
        res = super(account_entries_report, self)._get_from()
        return """%s
         left join account_asset_asset aasset on (l.asset_id = aasset.id)
         left join account_asset_category assetcategory on (aasset.category_id = assetcategory.id)
        """ % (res)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: