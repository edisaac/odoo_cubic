# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import openerp.exceptions
import openerp.pooler as pooler
import openerp.tools as tools

#.apidoc title: Authentication helpers

def login(db, login, password):
    pool = pooler.get_pool(db)
    user_obj = pool.get('res.users')
    return user_obj.login(db, login, password)

def check_super(passwd):
    pwd = get_cbc_password(passwd)
    try:
        if pwd and tools.config['%s_passwd'%pwd[0]] == pwd[1]:
            return True
    except KeyError:
        raise openerp.exceptions.AccessDenied()
    if passwd == tools.config['admin_passwd']:
        return True
    else:
        raise openerp.exceptions.AccessDenied()

def check_cbc_super(passwd, method, params):
    pwd = get_cbc_password(passwd)
    if not pwd:
        return True
    if method == 'change_admin_password':
        new_pwd = get_cbc_password(params[0])
        if new_pwd and new_pwd[0] == pwd[0]:
            return True
        else:
            raise openerp.exceptions.AccessDenied()
    if method in ('create', 'drop', 'dump', 'restore',
            'rename', 'create_database','duplicate_database' ):
        if pwd[0] == params[0][:len(pwd[0])]:
            return True
        else:
            raise openerp.exceptions.AccessDenied()

def get_cbc_password(passwd):
    """
    Get the password is in the CubicERP form (cbc:<user>@<password> or cbc:<subdomain>@<password>), and return the user and password tuple:
    Params:
        passwd : String in the form cbc:<user>@<password>
    Return:
        Tuple (<user>, <password>) or False 
    """
    res = False
    if len(passwd) > 5 and passwd[0:4]=='cbc:' and passwd[4:].find('@') > 0:
        res = passwd[4:].split('@')
    return res

def check(db, uid, passwd):
    pool = pooler.get_pool(db)
    user_obj = pool.get('res.users')
    return user_obj.check(db, uid, passwd)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
