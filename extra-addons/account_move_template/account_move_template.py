# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class account_move_template(osv.osv):

    _inherit = 'account.document.template'
    _name = 'account.move.template'

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'template_line_ids': fields.one2many('account.move.template.line', 'template_id', 'Template Lines'),
        }

account_move_template()

class account_move_template_line(osv.osv):

    _name = 'account.move.template.line'
    _inherit = 'account.document.template.line'

    _columns = {
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete="cascade"),
        'move_line_type':fields.selection([
            ('cr','Credit'),
            ('dr','Debit'),
            ], 'Move Line Type', required=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', ondelete="cascade"),
        'template_id': fields.many2one('account.move.template', 'Template'),
        }

    _sql_constraints = [
        ('sequence_template_uniq', 'unique (template_id,sequence)', 'The sequence of the line must be unique per template !')
    ]

account_move_template_line()
