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
import time

class account_table(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code']+': '+name
            res.append((record['id'], name))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of account for searching
                operand1,operand2 = name.split(': ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = 'account.table'
    _description = 'Account Table of Tables'
    _columns = {
            'company_id' : fields.many2one('res.company','Company', select=True),
            'code' : fields.char('Code', size=32, select=True, required=True),
            'name': fields.char('Name', size=2048, required=True, translate=True, select=True),
            'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Name'),
            'description': fields.text('Table Description'),
            'parent_id': fields.many2one('account.table','Parent Table', select=True, domain=[('type','=','view')]),
            'child_ids': fields.one2many('account.table', 'parent_id', string='Child Tables'),
            'type': fields.selection([('view','View'), ('normal','Normal')], 'Table Type'),
            'active': fields. boolean('Active'),
            'element_ids': fields.one2many('account.element','table_id',string="Elements"),
            'tax_ids' : fields.many2many('account.tax','account_table_tax','table_id','tax_id','Taxes')
            
        }
    _defaults = {
            'active' : True,
        }
    _sql_constraints = [('code_unique','unique(company_id,code)',_('The code must be unique!'))]

    _order = "code"
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from account_table where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, _('Error ! You can not create recursive table of tables.'), ['parent_id'])
    ]
    def child_get(self, cr, uid, ids):
        return [ids]

account_table()

class account_element(osv.osv):
    _name = 'account.element'
    _description = 'Elements in table of tables'
    _columns = {
            'table_id': fields.many2one('account.table','Account Table',select=True),
            'name': fields.char('Element Code', size=64, select=True, required=True),
            'description': fields.text('Element Description'),
            'element_char': fields.char('Element String', size=1024),
            'element_float': fields.float('Element Float'),
            'element_percent': fields.float('Element Percent'),
            'start_date': fields.date('Start Date'),
            'end_date': fields.date('End Date'),
            'active': fields.boolean('Active'),
        }
    _defaults = {
            'active' : True,
        }
    _sql_constraints = [('table_name_unique','unique(table_id,name)',_('The element code must be unique for this table!'))]
    
    def get_element(self, cr, uid, table_code, element_code, field, date=None, context={}):
        sql = "select e.%s from account_element e,account_table t where e.table_id=t.id and t.active=True and e.active=True and t.type<>'view' and t.code='%s' and e.name='%s'"%(field,table_code,element_code)
        if date: sql += " and coalesce(start_date,'%s')<='%s' and coalesce(end_date,'%s')>='%s'"%(date,date,date,date)
        cr.execute(sql)
        return cr.fetchone()

    def get_elements(self, cr, uid, table_code, field, date=None, context={}):
        sql = "select e.%s from account_element e,account_table t where e.table_id=t.id and t.type<>'view' and t.active=True and e.active=True and t.code='%s'"%(field,table_code)
        if date: sql += " and coalesce(start_date,'%s')<='%s' and coalesce(end_date,'%s')>='%s'"%(date,date,date,date)
        cr.execute(sql)
        return [x[0] for x in cr.fetchall()]
    
    def browse_elements(self, cr, uid, table_code, date=time.strftime('%Y-%m-%d'), context={}):
        return self.browse(cr,uid,self.get_elements(cr,uid,table_code,'id',date=date,context=context),context=context)

    def exists(self, cr, uid, table_code, element_code, date=time.strftime('%Y-%m-%d'), context={}):
        return bool(self.get_element(cr,uid,table_code,element_code,'id',date=date,context=context))
    
    def get_element_percent(self, cr, uid, table_code, element_code, date=time.strftime('%Y-%m-%d'), context={}):
        val = self.get_element(cr,uid,table_code,element_code,'element_percent',date=date,context=context)
        return val and val[0] or 0.0

    def get_element_float(self, cr, uid, table_code, element_code, date=time.strftime('%Y-%m-%d'), context={}):
        val = self.get_element(cr,uid,table_code,element_code,'element_float',date=date,context=context)
        return val and val[0] or 0.0

    def get_element_char(self, cr, uid, table_code, element_code, date=time.strftime('%Y-%m-%d'), context={}):
        val = self.get_element(cr,uid,table_code,element_code,'element_char',date=date,context=context)
        return val and val[0] or ''
        
account_element()
