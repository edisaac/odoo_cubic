# -*- coding: utf-8 -*-
##############################################################################
#
#    school module for OpenERP
#    Copyright (C) 2010 Tecnoba S.L. (http://www.tecnoba.com)
#       Pere Ramon Erro Mas <pereerro@tecnoba.com> All Rights Reserved.
#
#    This file is a part of school module
#
#    school OpenERP module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    school OpenERP module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import osv, fields, orm
from tools.translate import _
from datetime import datetime

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'
_ADMIN_USER=1

class contact_type_annotation(osv.osv):
    _name = 'contact.type_annotation'
contact_type_annotation()


class contact_annotation_type_group_access(osv.osv):
    _name = 'contact.annotation_type.group_access'

    def name_get(self, cr, uid, ids, context=None):
        ret=[]
        for item in self.browse(cr, uid, ids, context=context):
            ret.append((item.id, "%s - %s" % (item.contact_type_annotation_id.name, group_id.name)))
        return ret

    _columns = {
        'contact_type_annotation_id': fields.many2one('contact.type_annotation', 'Type', required=True),
        'group_id': fields.many2one('res.groups', 'Group'),
        'perm_read': fields.boolean('Read Access'),
        'perm_write': fields.boolean('Write Access'),
        'perm_create': fields.boolean('Create Access'),
        'perm_unlink': fields.boolean('Delete Permission'),
    }

    _sql_constraints = [('anno_type_group_access_unique','unique(contact_type_annotation_id,group_id)','Each annotation type must have only one group.')]

contact_annotation_type_group_access()

class contact_annotation_function(osv.osv):
    _name = 'contact.annotation.function'
    _columns = {
        'name': fields.char('Function name', translate=True, size=64,),
        'code': fields.char('Code',size=10,),
        'ref' : fields.char('Ref',size=20,),
    }
contact_annotation_function()

class contact_state(osv.osv):
    _name = 'contact.annotation.state'
    _columns = {
        'name': fields.char('Contact state name', size=64, translate=True, ),
        'code': fields.char('State code', size=20, required=True),
        'valid': fields.boolean('Valid',),
        'group_ids': fields.many2many('res.groups','groups_contact_states_rel','state_id','group_id',string='Groups',help='Groups that can view the status'),
        'function_ids': fields.many2many('contact.annotation.function','function_and_state_rel','state_id','function_id',string='Functions',help="Partners can view the status over contact with these functions.")
    }

    _defaults = {
        'valid': lambda *a: True,
    }

    def _code_without_comas(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids):
            if item.code.find(',')>=0: return False
        return True

    _sql_constraints = [('code_annotation_state_unique','unique(code)','Code must be unique')]
    _constraints = [(_code_without_comas,"The code must'n have comas",['code'])]

    def name_get(self, cr, uid, ids, context=None):
        res=[]
        for item in self.browse(cr, uid, ids, context=context):
            if item.name:
                res.append( (item.id, item.name) )
            else:
                res.append( (item.id, item.code) )
        return res

    def _get_selection(self, cr, uid, context=None):
        ret=[]
        for item in self.read(cr, uid, self.search(cr, uid, [])):
            ret.append( (item['code'],item['name'] ) )
        return ret

    def create_if_not_exists(self, cr, uid, vals, context=None):
        ret=self.search(cr, uid, [('code','=',vals['code'])], context=context)
        if not ret:
            return self.create(cr, uid, vals, context=context)
        else:
            return ret[0]

contact_state()

class contact_state_range2(osv.osv_memory):
    _name='contact.state_range2'

    def _annotation_for_state_range(self, cr, uid, ids, field_name, args, context=None):
        ret={}
        for item in self.browse(cr, uid, ids, context=context):
            anno_type_ids=self.pool.get('contact.type_annotation').search(cr, uid, [('states','ilike','%s' % item.lstate.code)])
            anno_ids=self.pool.get('contact.annotation').search(cr, uid, [('anno_type','in',anno_type_ids),('contact_id','=',item.contact_id.id),('valid_to','>',item.datetime_from),('valid_from','<',item.datetime_to)], order='creation_date desc')
            ret[item.id]=anno_ids
        return ret

    _columns={
        'annotation_ids': fields.function(_annotation_for_state_range, type='one2many', obj='contact.annotation', method=True, string='Annotations',),
        'lstate': fields.many2one('contact.annotation.state','State',required=True,select=1,),
        'datetime_from': fields.datetime('From',select=1),
        'datetime_to': fields.datetime('To',select=1),
        'contact_id': fields.many2one('res.partner.contact','Contact',select=1,),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ret=[]

        # States criteria
        state_ids=None
        lstate_leafs=[]
        for (field,op,expr) in args:
            field_parts=field.split('.',1)
            if field_parts[0]=='lstate':
                field2='code'
                if len(field_parts)>1:
                    field2=field_parts[1]
                lstate_leafs+=[(field2,op,expr)]
        if lstate_leafs:
            state_ids=self.pool.get('contact.annotation.state').search(cr, uid, lstate_leafs, context=context)

        # Contacts criteria
        contact_ids=None
        contact_leafs=[]
        for (field,op,expr) in args:
            field_parts=field.split('.',1)
            if field_parts[0]=='contact_id':
                field2='name'
                if len(field_parts)>1:
                    field2=field_parts[1]
                contact_leafs+=[(field2,op,expr)]
        if contact_leafs:
            contact_ids=self.pool.get('res.partner.contact').search(cr, uid, contact_leafs, context=context)
        state_ranges=self.pool.get('contact.annotation').get_range_states(cr, uid, contact_ids=contact_ids, state_ids=state_ids, date_from=None, date_to=None, context=None)
        for ((state,contact_id),ranges) in state_ranges.items():
            for range in ranges:
                if range['op']=='+':
                    state_ids=self.pool.get('contact.annotation.state').search(cr, uid, [('code','=',state)])
                    if not state_ids: continue
                    ret.append( self.create(cr, uid, {'lstate': state_ids[0], 'contact_id': contact_id, 'datetime_from': range['date_from'], 'datetime_to': range['date_to']}) )
        return ret
    
    _sql_constraints = []
    
contact_state_range2()


class contact_partner_function(osv.osv):
    _name = 'contact.partner.function'
    _log_access = True

    # TODO?: Access rules:
    #    Manager group can access all registers
    #    Others users can access contact or partner related with user or created by user.

    def _name_get(self, cr, uid, ids, context=None):
        ret=[]
        for obj in self.browse(cr, uid, ids):
            ret.append(obj.id, "%s - %s - %s" % (obj.contact_id.name, obj.partner_id.name, function.name))
        return ret
        
    _columns = {
        'contact_id': fields.many2one('res.partner.contact','Contact',),
        'partner_id': fields.many2one('res.partner','Partner',),
        'function_id': fields.many2one('contact.annotation.function','Function',),
    }

contact_partner_function()

class contact_annotation_type_function_access(osv.osv):
    _name = 'contact.annotation_type.function_access'

    def name_get(self, cr, uid, ids, context=None):
        ret=[]
        for item in self.browse(cr, uid, ids, context=context):
            ret.append((item.id, "%s - %s" % (item.contact_type_annotation_id.name, function_id.name)))
        return ret

    _columns = {
        'contact_type_annotation_id': fields.many2one('contact.type_annotation', 'Type', required=True),
        'function_id': fields.many2one('contact.annotation.function', 'Function'),
        'perm_read': fields.boolean('Read Access'),
        'perm_write': fields.boolean('Write Access'),
        'perm_create': fields.boolean('Create Access'),
        'perm_unlink': fields.boolean('Delete Permission'),
    }

    _sql_constraints = [('anno_type_function_access_unique','unique(contact_type_annotation_id,function_id)','Each annotation type must have only one function.')]

contact_annotation_type_function_access()

class contact_type_annotation(osv.osv):
    _name = 'contact.type_annotation'
contact_type_annotation()

class contact_type_and_state(osv.osv):
    _name = 'contact.anno_type.state'
    _columns = {
        'anno_type': fields.many2one('contact.type_annotation','Annotation type',ondelete='cascade',),
        'op' : fields.boolean('Operation',help='True add the state, False remove the state'),
        'state_id': fields.many2one('contact.annotation.state','State',ondelete='cascade',)
    }

contact_type_and_state()

class contact_type_annotation(osv.osv):
    _name = 'contact.type_annotation'

    def _states(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for anno_type in self.browse(cr, uid, ids,context=context):
            ret[anno_type.id]=''
            for data_state in anno_type.data_states:
                if len(ret[anno_type.id])>0: ret[anno_type.id]+=','
                if data_state.op: ret[anno_type.id]+='+'
                else: ret[anno_type.id]+='-'
                ret[anno_type.id]+=data_state.state_id.code
        return ret

    def normalize_states(self, cr, uid, states, context=None):
        ret_list=[]
        return ','+','.join(ret_list)+','

    def _save_states(self, cr, uid, id, name, value, fnct_inv, arg, context=None):
        if not context: context={}
        if context.get('_saving_states',False):
            return True
        ids_to_unlink=self.pool.get('contact.anno_type.state').search(cr, uid, [('anno_type','=',id)])
        self.pool.get('contact.anno_type.state').unlink(cr, uid, ids_to_unlink)
        for state in value.split(','):
            if not state: continue
            if state[0] not in ('-','+'): state='+'+state[1:]
            state_id=self.pool.get('contact.annotation.state').create_if_not_exists(cr, uid, {'code': state[1:]})
            self.pool.get('contact.anno_type.state').create(cr, uid, {'anno_type': id, 'op': (state[0]=='+'), 'state_id': state_id}, context={'_saving_states': True})
        return  True



    _columns = {
        'name' : fields.char('Name', size=30, translate=True, ),
        'code' : fields.char('Code', size=5, ),
        'perms_functions' : fields.one2many('contact.annotation_type.function_access','contact_type_annotation_id',string='Informer functions',help='Perms for informer function over contact to create that annotation type'),
        'perms_groups' : fields.one2many('contact.annotation_type.group_access', 'contact_type_annotation_id', string='Groups', help='Group which users could create and modify that annotation type',),
        'states' : fields.function(_states, fnct_inv=_save_states, method=True, string='States', type='char', size=150, help="States (letters from A-Z, words separates with comas, prefix - if retire state of annotations superseded. )",
            store={
                'contact.type_annotation': ( lambda self, cr, uid, ids, context: ids , ['data_states'], 10),
                'contact.anno_type.state': ( lambda self, cr, uid, ids, context: [x['anno_type'][0] for x in self.read(cr, uid, ids, ['anno_type'])] , ['op','state_id'], 20),
            } ),
        'data_states': fields.one2many('contact.anno_type.state','anno_type',),
    }

    def _get_gids(self, cr, uid):
        cr.execute("select gid from res_groups_users_rel where uid=%s", (uid,))
        return [x[0] for x in cr.fetchall()]

    def get_type_annotations(self, cr, uid, contact_ids=None, task='read', context=None):
        if task not in ('read','write','create','unlink'): task='read'
        if type(contact_ids)!=type([]): contact_ids=[]
        if type(contact_ids)!=type({}): context={}
        group_access_ids=self.pool.get('contact.annotation_type.group_access').search(cr, uid, [('group_id','in',self._get_gids(cr, uid)),('perm_'+task,'=',True)])
        search_args=['|',('perms_groups','in',group_access_ids)]
        if contact_ids:
            functions={}
            partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)], context=context)
            rel_ids=self.pool.get('contact.partner.function').search(cr, uid, [('partner_id','in',partner_ids),('contact_id','in',contact_ids),], context=context)
            for item in self.pool.get('contact.partner.function').read(cr, uid, rel_ids, ['contact_id','function_id'] ):
                if item['function_id'][0] not in functions: functions[item['function_id'][0]]=[]
                functions[item['function_id'][0]].append(item['contact_id'][0])
            functions_to_search=[]
            for (function_id, contact_ids2) in functions.items():
                if len(contact_ids)==len(contact_ids2):
                    functions_to_search.append(function_id)
            function_access_ids=self.pool.get('contact.annotation_type.function_access').search(cr, uid, [('function_id','in',functions_to_search),('perm_'+task,'=',True)])
            search_args+=[('perms_functions','in',function_access_ids+[0])]
        ret=self.search(cr, uid, search_args, context=context)
        return ret


contact_type_annotation()

class contact_annotation(osv.osv):
    _name = 'contact.annotation'

    def name_get(self, cr, uid, ids, context={}):
        res=[]
        for item in self.browse(cr, uid, ids):
            res.append((item.id, '%s,%s,%s-%s' % (item.contact_id.name,item.anno_type.name,item.valid_from,item.valid_to)))
        return res
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        contact_ids=self.pool.get('res.partner.contact').search(cr, uid, [('name','ilike',name)], limit=limit, context=context)
        type_ids=self.pool.get('contact.type_annotation').search(cr, uid, [('name','ilike',name)], limit=limit, context=context)
        ids=self.search(cr, uid, ['|',('contact_id','in',contact_ids),('anno_type','in',type_ids)], limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    _columns = {
        'user_id': fields.many2one('res.users', 'Responsible'),
        'partner_id': fields.related('contact_id','job_ids','address_id','partner_id',type='many2one',\
                         relation='res.partner', string='Main Employer'),
        'contact_id' : fields.many2one('res.partner.contact', 'Contact', required=True, ondelete="cascade", select=True,),
        'anno_type' : fields.many2one('contact.type_annotation', 'Type', required=True, ondelete="restrict", select=True, ),
        'valid_from' : fields.datetime('Valid from',select=1,required=True,),
        'valid_to' : fields.datetime('Valid to',select=1,required=True,),
        'comment' : fields.text('Commment'),
        'informer' : fields.many2one('res.partner', 'Informer', ondelete="restrict", select=True, ),
        'creation_date' : fields.datetime('Creation date', required=True, ),
    }

    _order="creation_date desc"
    
    _sql_constraints=[('date_interval_ok','CHECK (valid_to>valid_from)','Date from must to be minor than date to'),]

    _defaults={
        'creation_date' : lambda *a: datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id' : lambda self,cr,uid,context: uid,
        }

    def check_perms(self, cr, uid, ids, task, context=None):
        if not ids or task not in ('read','write','unlink','create'): return []
        user=self.pool.get('res.users').browse(cr, uid, uid)
        group_ids=[x.id for x in user.groups_id]+[0]
        
        partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)])+[0]
        
        query="""
            SELECT DISTINCT a.id FROM contact_annotation AS a
                     INNER JOIN contact_type_annotation AS ta ON a.anno_type=ta.id
                     LEFT JOIN contact_partner_function AS cpf ON cpf.contact_id=a.contact_id AND cpf.partner_id IN %%s
                     LEFT JOIN contact_annotation_type_group_access AS ga ON ta.id=ga.contact_type_annotation_id AND ga.perm_%s='t' AND group_id IN %%s
                     LEFT JOIN contact_annotation_type_function_access AS fa ON ta.id=fa.contact_type_annotation_id AND fa.perm_%s='t' AND fa.function_id=cpf.function_id
            WHERE a.id IN %%s AND (ga.id IS NOT NULL OR fa.id IS NOT NULL OR ( (a.user_id=%%s OR a.informer IN %%s) AND '%s'='read'))
        """ % (task,task,task)
        cr.execute(query, (tuple(partner_ids), tuple(group_ids), tuple(ids), uid, tuple(partner_ids), ) )
        return [x[0] for x in cr.fetchall()]
        
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ret=super(contact_annotation, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        if ret and type(ret)!=type([]):
            ret=[ret]
        ret=self.check_perms(cr, uid, ret, 'read', context=context)
        return ret
        
    def write(self, cr, uid, ids, vals, context=None):
        fields_updatables=['comment']
        for key in vals.keys():
            if key not in fields_updatables: del vals[key]
        if not vals: return True
        return super(contact_annotation, self).write(cr, uid, ids, vals, context=context)


    def create(self, cr, uid, vals, context=None):
        ret=super(contact_annotation, self).create(cr, uid, vals, context=context)
        ids_with_perms=self.check_perms(cr, uid, [ret], 'write', context=context)
        if ret not in ids_with_perms:
            raise orm.except_orm(_('Error'), _('Not granted!'))
        return ret

    def unlink(self, cr, uid, ids, context=None):
        ids_with_perms=self.check_perms(cr, uid, ids, 'unlink', context=context)
        for x in ids:
            if x not in ids_with_perms:
                raise orm.except_orm(_('Error'), _('Not granted!'))
        return super(contact_annotation, self).unlink(cr, uid, ids, context=context,)

    def read(self, cr, uid, ids, fields=None, context=None, load=None):
        ids_with_perms=self.check_perms(cr, uid, ids, 'read', context=context)
        for x in ids:
            if x not in ids_with_perms:
                raise orm.except_orm(_('Error'), _('Not granted!'))
        return super(contact_annotation, self).read(cr, uid, ids, fields=fields, context=context)
       

    def _min(self,a,b):
        if a<b: return a
        else: return b

    def _max(self,a,b):
        if a>b: return a
        else: return b

    def incorpora_interval(self, intervals, interval):
        """
        Paràmetres:
          En intervals tindrem els intervals consecutius de temps ordenats de menor a major
        data amb diccionari de data inici, data fi, l'operació que té l'estat i la data d'efectivitat de l'estat.
        Date_to de l'interval anterior ha de ser igual al date_from del següent.
        Amb 'op':'+' l'estat hi és present i 'op':'-' no hi és present.
          En interval tindrem l'interval del nou estat que i la operació '+' o '-' que marcarà si volem afegir o treure l'estat. També en informarà de l'efectivitat de l'estat. L'anomenarem interval a tractar.
        Funció:
          Refà la llista d'intervals incorporant l'interval passat de la forma que s'explica en el codi
        Retorna:
          Una nova llista d'intervals booleans temporals ordenats amb data d'efectivitat
        """
        new_ranges=[] # la nova llista d'intervals que retornarem
        for range in intervals: # repassem els intervals un a un
            if range['date_from']>interval['date_to']: break # intervals es troba ordenat i ja aquest ni els següents a repassar tocaran al quin tractem, per tant, trequem el bucle
            # demanem si l'interval a tractar toca en el temps a l'interval de la llista que repassem
            # a més, l'efectivitat ha de ser més actual, perquè si és més antiga, tampoc canviarem l'interval que repassem.
            if range['date_to']<=interval['date_from'] or range['date_from']>=interval['date_to'] or range['creation_date']>interval['creation_date']:
                # l'interval a tractar no toca l'interval que repassem, per tant l'afegim sense fer cap operació sobre ell
                # Noteu que es manté l'ordenació, la operació i l'efectivitat.
                new_ranges.append(range)
            else:
                # l'interval a tractar toca en el temps a aquest interval que repassem
                # anem a comprovar si queda algún tros de l'interval que repassem a l'esquerra del quin tractem...
                if interval['date_from']>range['date_from']:
                    # doncs, si. Queda l'interval desde l'inici d'aquest interval que repassem fins a l'inici de l'interval a tractar que volem incloure
                    new_ranges.append({
                        'date_from': range['date_from'],
                        'date_to': interval['date_from'],
                        'creation_date': range['creation_date'], 'op': range['op']})
                # afegim ara l'interval que queda en mig. L'inici serà el major entre l'inici de l'interval a repassar o l'inici de l'interval a tractar
                # Observeu:
                # - aquest interval sempre hi serà: hem comprovat que l'interval a tractar toca amb el quin repassem i té una efectivitat major
                # - aquest interval que sempre quedarà encadenat amb l'interval anterior:
                #    ; si existeix marge a l'esquerra entre l'interval que repassem i quin tractem, l'inici de l'interval que afegim serà l'inici del quin tractem que és el final que quin em afegit en la condició anterior
                #    ; si no existeix marge a l'esquerra, l'inici de l'interval serà el mateix que quin repassem
                #   així doncs, podem trobar directament l'inici d'aquest interval trobant el màxim entre els dos valors.
                # en el fi podem seguir el mateix raonament, però invertit
                # la operació serà la quina ens marqui l'interval i marcarem l'efectivitat de l'interval per següents inclusions d'altres intervals a tractar si es el cas
                new_ranges.append({
                    'date_from': self._max(range['date_from'], interval['date_from']),
                    'date_to': self._min(range['date_to'], interval['date_to']),
                    'creation_date': interval['creation_date'], 'op': interval['op']})
                # anem a comprovar si queda algún tros de l'interval que repassem a la dreta del quin tractem...
                if interval['date_to']<range['date_to']:
                    # doncs, si. Queda l'interval desde l'inici de l'interval a tractar que volem incloure fins a la fi d'aquest interval que repassem
                    new_ranges.append({
                        'date_from': interval['date_to'],
                        'date_to': range['date_to'],
                        'creation_date': range['creation_date'], 'op': range['op']})
        return new_ranges

    def get_contacts(self, cr , uid, context=None):
        if not context: context={}
        partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)], context=context)
        search_args= [('partner_id','in',partner_ids),]
        if 'function' in context:
            function_ids=self.pool.get('contact.annotation.function').search(cr, uid, [('name','ilike',context['function'])])
            search_args+= [('function_id','in',function_ids)]
        rel_ids=self.pool.get('contact.partner.function').search(cr, uid, search_args, context=context)
        return [item['contact_id'][0] for item in self.pool.get('contact.partner.function').read(cr, uid, rel_ids, ['contact_id'])]

    def get_states(self, cr, uid, context=None):
        cr.execute("""
SELECT DISTINCT s.id FROM contact_annotation_state AS s
   INNER JOIN groups_contact_states_rel AS sgr ON s.id=sgr.state_id
   INNER JOIN res_groups_users_rel AS gu ON gu.gid=sgr.group_id
   WHERE gu.uid=%s""", (uid,))
        return [x[0] for x in cr.fetchall()]

    def get_contacts_for_state(self, cr , uid, state_ids, contact_ids, context=None):
        ret={}
        query="""
SELECT DISTINCT cpf.contact_id,fs.state_id  FROM res_partner AS p, contact_partner_function AS cpf, function_and_state_rel AS fs
   WHERE p.user_id=%s AND cpf.partner_id=p.id AND fs.function_id=cpf.function_id"""
        params=[uid]
        if state_ids:
            query+=" AND fs.state_id IN %s"
            params.append( tuple(state_ids) )
        if contact_ids:
            query+=" AND cpf.contact_id IN %s"
            params.append( tuple(contact_ids) )            
        cr.execute(query, params)
        for (contact_id,state_id) in cr.fetchall():
            if state_id not in ret: ret[state_id]=[]
            if contact_id not in ret[state_id]: ret[state_id].append(contact_id)
        return ret


    def get_range_states(self, cr, uid, contact_ids=None, state_ids=None, date_from=None, date_to=None, context=None):
        """
        Els intervals d'estat dels estats que com a integrant del grup pot
        veure + Els intervals d'estat sobre contactes en els que l'usuari-partner
        té funcions previstes en la definició de l'estat . 
        """
        if not context: context={}



        tables="contact_annotation AS a, contact_type_annotation AS ta, contact_anno_type_state AS ats"
        where="a.anno_type=ta.id AND ats.anno_type=ta.id AND ("
        params=[]
        
        """
        Que apareguin tots per als quins els grups de l'usuari té permisos i estiguin en la llista de filtre si existeix.
        """
        state_ids2=self.get_states(cr, uid, context=context)
        if type(state_ids)!=type(None):
            for x in list(state_ids2):
                if x not in state_ids: state_ids2.remove(x)
        if state_ids2:
            where+="ats.state_id IN %s"
            params.append(tuple(state_ids2))
        else:
            where+='false'
            
        contacts_for_state=self.get_contacts_for_state(cr, uid, state_ids, contact_ids, context=context)
        if contacts_for_state:
            partner_ids=self.pool.get('res.partner').search(cr, uid, [('user_id','=',uid)])
            if partner_ids:
                tables+=', contact_partner_function AS cpf, function_and_state_rel AS fs '
                where='cpf.partner_id IN %s AND cpf.contact_id=a.contact_id AND cpf.function_id=fs.function_id AND ' % (tuple(partner_ids+[0]),) + where
                for (state_id, contact_ids2) in contacts_for_state.items():
                    where+=" OR (fs.state_id=%s AND a.contact_id IN %s)"
                    params+=[state_id,tuple(contact_ids2)]
        where+=")"

        if date_to:
            where+=" AND valid_from<%s"
            params+=[date_to]
        if date_from:
            where+=" AND valid_to>%s"
            params+=[date_from]

        query="SELECT DISTINCT a.id FROM %s WHERE %s" % (tables,where)
        cr.execute(query, params)
        anots=[x[0] for x in cr.fetchall()]
        # Build state ranges
        dict_ranges={}
        for anno in self.browse(cr, _ADMIN_USER, anots):
            for data_state in anno.anno_type.data_states:
                op='+'
                if not data_state.op: op='-'
                if data_state.state_id.id in state_ids2 or data_state.state_id.id in contacts_for_state:
                    key=(data_state.state_id.code,anno.contact_id.id)
                    if key not in dict_ranges:
                        dict_ranges[key]=[{'date_from': date_from or _MIN_DATETIME, 'date_to': date_to or _MAX_DATETIME, 'creation_date': '0000-00-00', 'op': '-'}]
                    dict_ranges[key]=self.incorpora_interval(dict_ranges[key], {'date_from': anno.valid_from, 'date_to': anno.valid_to, 'creation_date': anno.creation_date, 'op': op})

        # Build data struct to return
        # @type dict_ranges dict
        ret={}
        for (key,value) in dict_ranges.items():
            new_list=[]
            counter=0
            for item in value:
                if not new_list:
                    new_list.append({'date_from': item['date_from'], 'date_to': item['date_to'], 'op': item['op']})
                else:
                    if new_list[counter]['op']==item['op']:
                        new_list[counter]['date_to']=item['date_to']
                    else:
                        new_list.append({'date_from': item['date_from'], 'date_to': item['date_to'], 'op': item['op']})
                        counter+=1
            ret[key]=[]
            for item in new_list:
                if item['op']=='+' or context.get('complete_intervals',False):
                    ret[key].append(item)
        if context.get('complete_intervals',False):
            for contact_id in contact_ids:
                for state in the_states:
                    if (state,contact_id) not in ret:
                        ret[(state,contact_id)]=[{'date_from': date_from, 'date_to': date_to, 'op': '-'}]

        return ret


contact_annotation()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
