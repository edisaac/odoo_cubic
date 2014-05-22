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

from osv import osv, fields

_MIN_DATETIME='1970-01-01 00:00:00'
_MAX_DATETIME='2099-12-31 23:59:59'

def agafa_id(unid):
    if type(unid)==type(tuple()):
        return unid[0]
    return unid

class groups_group(osv.osv):
    _name = 'groups.group'

groups_group()

class groups_participation(osv.osv):
    _name = 'groups.participation'

groups_participation()

class groups_group_assignation(osv.osv):
    _name = 'groups.group_assignation'

    _columns =  {
        'group_id' : fields.many2one('groups.group','Group', required=True,
            select=1, ondelete='cascade',),
        'participation_id' : fields.many2one('groups.participation', 'Participation',
            required=True, select=1, ondelete='cascade'),
        'datetime_from' : fields.datetime('Begining', select=1,),
        'datetime_to' : fields.datetime('End', select=1,),
    }

    _sql_constraints = [('dates_ok','CHECK (datetime_to>=datetime_from)','Date to minor than date from'),]


    def _assignation_in_domain(self, cr, uid, ids):
        data=self.read(cr, uid, ids, ['group_id','participation_id','datetime_from','datetime_to'], context={'withoutBlank': False})
        gids=set()
        for item in data:
            if item['datetime_from']!=item['datetime_to']: gids.add(item['group_id'])
        domains=self.pool.get('groups.group')._domain_assignations(cr, uid, list(gids))
        if domains:
            for item in data:
                group_id=item['group_id']
                participation_id=item['participation_id']
                if (group_id not in domains) or (domains[group_id] is None): continue
                # No participation in domain group
                if not participation_id in domains[group_id]: return False
                interval_into=(item['datetime_from'],item['datetime_to'])
                ret=False
                for interval_domain in domains[group_id][participation_id]:
                    if interval_into[0]>=interval_domain[0] and interval_into[1]<=interval_domain[1]: ret=True
                # No inclusive intervals in domain group for participation_id
                if not ret: return False
        return True

    _constraints = [
        (_assignation_in_domain, 'Assignation out of domain!', ['datetime_from','datetime_to']),
        ]

    def _join(self, cr, uid, ids):
        """
        Per cada assignació de la llista passada pels identificadors, 
        ajunta les assignacions laterals amb la mateixa classificació.
        Serveix per quan volem esborrar una assignació inclosa en una classificació i volem tapar el forat deixat.
        """
        query="""
        SELECT gac.id,gac.group_id,gac.datetime_to
        FROM groups_group_assignation AS ga
        INNER JOIN groups_group AS g ON ga.group_id=g.id
        INNER JOIN groups_parent_groups_rel AS gcr1 ON g.id=gcr1.son
        INNER JOIN groups_parent_groups_rel AS gcr2 ON gcr2.father=gcr1.father
        INNER JOIN groups_group AS gc ON gc.id=gcr2.son
        INNER JOIN groups_group_assignation AS gac ON gc.id=gac.group_id
            AND gac.participation_id=ga.participation_id
            AND (ga.datetime_to=gac.datetime_from OR ga.datetime_from=gac.datetime_to)
        WHERE ga.id in %(ids)s
        ORDER BY gac.datetime_from
        """
        cr.execute(query,{'ids': tuple(ids) })
        id_to_extends=0
        ids_to_unlink=[]
        groupy=None
        for (id, group_id, datetime_to) in cr.fetchall():
            if groupy and group_id==groupy:
                super(groups_group_assignation, self).write(cr, uid, [id_to_extends],
                    {'datetime_to': datetime_to})
                ids_to_unlink.append(id)
                break
            id_to_extends=id
            groupy=group_id
        super(groups_group_assignation, self).unlink(cr, uid, ids_to_unlink)

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids: return True
        context_unlinking=dict(context)
        context_unlinking.update({'unlinking':True})
        # ?
        self.write(cr, uid, ids, {}, context=context_unlinking)
        # Ajuntem les assignacions laterals amb la mateixa classificació
        self._join(cr, uid, ids)
        return super(groups_group_assignation, self).unlink(cr, uid, ids, context=context)

    def _cut(self, cr, uid, ga_id_to_cut, datetime_cut, ga_to_cut_datetime_to, ga_to_cut_group_id, ga_to_cut_participation_id):
        """
        Demanem retallar les assignacions dels subgrups i a continuació retallem l'assignacio que ens passen
        """
        sub_ids_to_cut=self.search(cr, uid, [
            ('participation_id','=',ga_to_cut_participation_id),
            ('group_id.parent_ids','=',ga_to_cut_group_id),
            ('datetime_from','<',datetime_cut),
            ('datetime_to','>',datetime_cut)])
        for item in self.read(cr, uid, sub_ids_to_cut,
                ['group_id','datetime_from','datetime_to'], context={'withoutBlank': False}):
            self._cut(cr, uid, ga_id_to_cut=item['id'], datetime_cut=datetime_cut, ga_to_cut_datetime_to=item['datetime_to'],
                ga_to_cut_group_id=item['group_id'][0], ga_to_cut_participation_id=ga_to_cut_participation_id)
        super(groups_group_assignation, self).write(cr, uid, ga_id_to_cut, {'datetime_to': datetime_cut})
        super(groups_group_assignation, self).create(cr, uid, {
            'group_id': ga_to_cut_group_id,
            'participation_id': ga_to_cut_participation_id,
            'datetime_from': datetime_cut,
            'datetime_to': ga_to_cut_datetime_to})


    def create(self, cr, uid, vals, context=None):
        #import pdb; pdb.set_trace()
        if not context: context = {}
        if 'datetime_from' not in vals: vals['datetime_from']=_MIN_DATETIME
        if 'datetime_to' not in vals: vals['datetime_to']=_MAX_DATETIME
        if not vals['datetime_from']: vals['datetime_from']=_MIN_DATETIME
        if not vals['datetime_to']: vals['datetime_to']=_MAX_DATETIME
        if vals['datetime_to']==vals['datetime_from']: return True
        """
        Hem de crear una nova assignacio. No hi ha problema excepte quan el grup de l'assignacio forma part d'una classificacio. En aquest cas, donem prioritat a la nova petició i retallem les assignacions existents.
        L'estrategia que seguirem sera crear un interval buit, retallant si fa falta les assignacions existents de la classificacio, i modificar-lo després amb el metode write que s'encarregara de modificar les assignacions laterals (en la linia de temps) de la classificacio.
        Si el contexte es extern cal mirar a on es crea la nova assignacio
        Si es crea enmig d'una altra assignacio de la mateixa classificacio,
            es retalla i a partir d'alla es crea una altra amb quedant la nova enmig.
            En aquest cas, si hi ha assignacions de subgrups, tambe s'han
            de retallar sense cap condicio.
        Si es crea al finalitzar o al comencar una altra assignacio de la mateixa classificacio, no es fa res.
        Despres, amb el write ja es fan la resta d'operacions.
        """
        group=self.pool.get('groups.group').browse(cr, uid, vals['group_id'], context=context)
        grups_mateixa_classificacio_ids=[vals['group_id']]# No hem d'afegir interval buit si ja existeix
        if group.classification:
            grups_mateixa_classificacio_ids+=self.pool.get('groups.group').search(cr, uid, [
                ('parent_ids','=',group.parent_ids[0].id),
                ('classification','=',group.classification)]) # Cerco els grups amb la mateixa classificacio
        ids=self.search(cr, uid, [
                ('group_id','in',grups_mateixa_classificacio_ids),
                ('participation_id','=',vals['participation_id']),
                ('datetime_from','<=',vals['datetime_from']),
                ('datetime_to','>=',vals['datetime_from'])]) # Cerca d'assignacions de la mateixa classificacio que comencen o acaben a l'inici de l'interval buit que necessitariem crear
        """
        Cal interval buit ? Si n'hi ha interval del mateix grup on comenca el
            nou interval que volem crear, no.
        Cal retallar cap interval ? Si no creem interval buit no. L'assignacio a
            retallar inclou exclusivament la data d'inici del nou interval
        """
        cal_interval_buit=True
        id=None
        # @type context dict
        new_context=context.copy()
        new_context['withoutBlank']=False
        for ga in self.read(cr, uid, ids, ['group_id','datetime_from','datetime_to'],
            context=new_context):
            if agafa_id(ga['group_id'])==agafa_id(vals['group_id']):
                # Tenim una assignació del mateix grup que inclou l'inici del que volem afegir
                cal_interval_buit=False
                if vals['datetime_to']>ga['datetime_to']:
                    id=ga['id'] # ens quedem amb l'identificador perquè hem de modificar aquesta assignació
                else:
                    return ga['id'] # L'asignació que volem crear ja es troba inclòs en una existent per al mateix grup i no cal modificar res
                break # ja no ens interessa més seguir mirant 
            if ga['datetime_from']<vals['datetime_from']\
                or ga['datetime_to']>vals['datetime_from']: # Hem trobat una assignacio que inclou l'interval buit que necessitem crear i l'haurem de retallar
                self._cut(cr, uid, ga_id_to_cut=ga['id'], datetime_cut=vals['datetime_from'],
                    ga_to_cut_datetime_to=ga['datetime_to'], ga_to_cut_group_id=ga['group_id'][0], ga_to_cut_participation_id=vals['participation_id'])
        # Pas final creem l'interval d'assignació buit si cal i modifiquem l'interval nou o el trobat
        new_context=context.copy()
        ids_grups_per_sota=self.pool.get('groups.group').search(cr, uid, [('parent_ids','=',vals['group_id']),('creation','>',0)])
        ids_a_sota=[]
        if cal_interval_buit:
            vals2=vals.copy()
            vals2.update({'datetime_to': vals['datetime_from']})
            id=super(groups_group_assignation, self).create(cr, uid, vals2, context=context) # creem interval buit amb el metode de la superclasse
            #TODO: Possiblement calgui crear interval buit als subgrups
            new_context['interval_creation']=id
            
            # a crear per sota
            for id_grup_per_sota in ids_grups_per_sota:
                vals3=vals.copy()
                vals3.update({'group_id': id_grup_per_sota})
                ids_a_sota.append( self.create(cr, uid, vals3, context=new_context) )
        self.write(cr, uid, [id]+ids_a_sota, {'datetime_to': vals['datetime_to']}, context=new_context)
        
        return id


    def read(self, cr, uid, ids, fields, context=None, load='_classic_write'):
        if not fields: fields=[]
        if not context: context={}
        ret=super(groups_group_assignation, self).read(cr, uid, ids, fields, context=context, load=load)
        # @type context dict
        if context.get('withoutBlank', True):
            # @type ret list
            for item in ret:
                if 'datetime_from' in item:
                    if item['datetime_from']==_MIN_DATETIME: item['datetime_from']=''
                if 'datetime_to' in item:
                    if item['datetime_to']==_MAX_DATETIME: item['datetime_to']=''
        return ret

    def amplio(self, cr ,uid, ga, datetime_from, datetime_to, context=None):
        ret=True
        if not context: context={}
        # primer modifico assignacions de classificacions laterals, després els meus limits i després modifico els fills
        if ga.group_id.classification and context.get('tracta_classificacions', True):
            # cerco assignacions de classificacions per l'esquerra
            ids_parcials=self.search(cr, uid, [('group_id.parent_ids','=',ga.group_id.parent_ids[0].id),('id','!=',ga.id),('group_id.classification','=',ga.group_id.classification),('participation_id','=',ga.participation_id.id)])
            ids_laterals_a_esborrar=[]
            new_context=context.copy().update({'tracta_classificacions': False});
            if datetime_from:
                ids_laterals_a_esborrar+=self.search(cr, uid, [('id','in',ids_parcials),('datetime_to','<=',ga.datetime_from),('datetime_from','>',datetime_from)])
                id_lateral_a_reduir_per_esquerra=self.search(cr, uid, [('id','in',ids_parcials),('id','not in',ids_laterals_a_esborrar),('datetime_to','<=',ga.datetime_from),('datetime_to','>',datetime_from)])
                self.write(cr, uid, id_lateral_a_reduir_per_esquerra, {'datetime_to': datetime_from}, context=new_context)
            if datetime_to:
                ids_laterals_a_esborrar+=self.search(cr, uid, [('id','in',ids_parcials),('datetime_from','>=',ga.datetime_to),('datetime_to','<',datetime_to)])
                id_lateral_a_reduir_per_dreta=self.search(cr, uid, [('id','in',ids_parcials),('id','not in',ids_laterals_a_esborrar),('datetime_from','>=',ga.datetime_to),('datetime_from','<',datetime_to)])
                self.write(cr, uid, id_lateral_a_reduir_per_dreta, {'datetime_from': datetime_to}, context=new_context)
            self.unlink(cr, uid, ids_laterals_a_esborrar, context=new_context)
        # ja tindria buits els laterals d'assignacions de la classificacio
        # ara amplio els limits de l'assignació actual
        if datetime_from:
            datetime_from_ant=ga.datetime_from
            # modifico limit per l'esquerra
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_from': datetime_from})
            # modifico fills
            id_fills_a_ampliar_esquerra=self.search(cr, uid, [('group_id.parent_ids','=',ga.id),('participation_id','=',ga.participation_id.id),('datetime_from','=',datetime_from_ant)])
            self.write(cr, uid, id_fills_a_ampliar_esquerra, {'datetime_from': datetime_from})
        if datetime_to:
            datetime_to_ant=ga.datetime_to
            # modifico limit per la dreta
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_to': datetime_to})
            # modifico fills
            id_fills_a_ampliar_dreta=self.search(cr, uid, [('group_id.parent_ids','=',ga.id),('participation_id','=',ga.participation_id.id),('datetime_to','=',datetime_to_ant)])
            self.write(cr, uid, id_fills_a_ampliar_dreta, {'datetime_to': datetime_to})
        return ret

    def redueixo(self, cr ,uid, ga, datetime_from, datetime_to, context=None):
        if not context: context={}
        ret=True
        # primer modifico els fills, després els meus límits i finalment acomodo les assignacions de classificacions laterals sempre que estiguin dins del seus dominis
        if datetime_from:
            ids_interiors_a_esborrar=self.search(cr, uid, [('group_id.parent_ids','=',ga.id),('participation_id','=',ga.participation_id.id),('datetime_from','<',datetime_from),('datetime_to','<=',datetime_from)])
            self.unlink(cr, uid, ids_interiors_a_esborrar , context=context)
            id_fill_a_reduir_esquerra=self.search(cr, uid, [('group_id.parent_ids','=',ga.id),('participation_id','=',ga.participation_id.id),('datetime_from','<',datetime_from),('datetime_to','>',datetime_from)])
            self.write(cr, uid, id_fill_a_reduir_esquerra, {'datetime_from': datetime_from})
            # TODO: Per poder treure la limitació d'assignacions no coincidents en els pares cal comprovar que la reducció dels fills sigui necessaria per la reducció del domini conjunt
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_from': datetime_from})
        if datetime_to:
            ids_interiors_a_esborrar=self.search(cr, uid, [('group_id.parent_ids','=',ga.id),('participation_id','=',ga.participation_id.id),('datetime_to','>',datetime_to),('datetime_from','>=',datetime_to)])
            self.unlink(cr, uid, ids_interiors_a_esborrar , context=context)
            id_fill_a_reduir_dreta=self.search(cr, uid, [('group_id.parent_ids','=',ga.id),('participation_id','=',ga.participation_id.id),('datetime_to','>',datetime_to),('datetime_from','<',datetime_to)])
            self.write(cr, uid, id_fill_a_reduir_dreta, {'datetime_to': datetime_to})
            # TODO: Per poder treure la limitació d'assignacions no coincidents en els pares cal comprovar que la reducció dels fills sigui necessaria per la reducció del domini conjunt
            ret&=super(groups_group_assignation, self).write(cr, uid, [ga.id], {'datetime_to': datetime_to})
        if ga.group_id.classification and context.get('tracta_classificacions', True):
            new_context=context.copy().update({'tracta_classificacions': False});
            # cerco assignacions de classificacions per l'esquerra
            if datetime_from:
                ga_classificacio_a_ampliar_esquerra=self.search(cr, uid, [('id','!=',ga.id),('participation_id','=',ga.participation_id.id),('group_id.parent_ids','=',ga.group_id.parent_ids[0].id),('group_id.classification','=',ga.group_id.classification),('datetime_to','=',ga.datetime_from)])
                self.write(cr, uid, ga_classificacio_a_ampliar_esquerra, {'datetime_to': datetime_from}, context=new_context)
            if datetime_from:
                ga_classificacio_a_ampliar_dreta=self.search(cr, uid, [('id','!=',ga.id),('participation_id','=',ga.participation_id.id),('group_id.parent_ids','=',ga.group_id.parent_ids[0].id),('group_id.classification','=',ga.group_id.classification),('datetime_from','=',ga.datetime_to)])
                self.write(cr, uid, ga_classificacio_a_ampliar_dreta, {'datetime_from': datetime_to}, context=new_context)
        return ret

        
    def write(self, cr, uid, ids, vals, context=None):
        ret=True
        if not ids: return ret # No cal fer res
        
        # Preparació de paràmetres amb valors per defecte
        if context is None:
            context = {}
        if not vals: vals={}
        if 'datetime_from' in vals:
            if not vals['datetime_from'] or vals['datetime_from']<_MIN_DATETIME:
                vals['datetime_from']=_MIN_DATETIME
        if 'datetime_to' in vals:
            if not vals['datetime_to'] or vals['datetime_to']>_MAX_DATETIME:
                vals['datetime_to']=_MAX_DATETIME

        if vals.has_key('datetime_from') or vals.has_key('datetime_to'):
            for ga in self.browse(cr, uid, ids):
                # casos
                if vals.get('datetime_from',ga.datetime_from)==vals.get('datetime_to',ga.datetime_to): # esborra
                    self.unlink(cr, uid, [ga.id], context=context)
                elif vals.get('datetime_from',ga.datetime_from)>ga.datetime_to or vals.get('datetime_to',ga.datetime_to)<ga.datetime_from:
                    self.unlink(cr, uid, [ga.id], context=context)
                    self.create(cr, uid, {'participation_id': ga.participation_id.id, 'group_id': ga.group_id.id, 'datetime_from': vals['datetime_from'], 'datetime_to': vals['datetime_to']}, context=context)
                else:
                    datetime_from_plus=None;datetime_to_plus=None
                    datetime_from_minus=None;datetime_to_minus=None
                    if vals.get('datetime_from',ga.datetime_from)<ga.datetime_from: datetime_from_plus=vals['datetime_from'] # amplia per la dreta
                    if vals.get('datetime_from',ga.datetime_from)>ga.datetime_from: datetime_from_minus=vals['datetime_from'] # redueix per la dreta
                    if vals.get('datetime_to',ga.datetime_to)>ga.datetime_to: datetime_to_plus=vals['datetime_to']# amplia per l'esquerra
                    if vals.get('datetime_to',ga.datetime_to)<ga.datetime_to: datetime_to_minus=vals['datetime_from'] # redueix per l'esquerra
                    ret&=self.amplio(cr, uid, ga, datetime_from_plus, datetime_to_plus)
                    ret&=self.redueixo(cr, uid, ga, datetime_from_minus, datetime_to_minus)
        else:
            ret&=super(groups_group_assignation, self).write(cr, uid, ids, vals, context=context)
        return ret

groups_group_assignation()

class groups_participation(osv.osv):
    _name = 'groups.participation'


    _columns = {
        'name' : fields.char('Ref',size=32),
        'participant' : fields.many2one('res.partner.contact', 'Participant',
            required=True, ondelete="cascade", select=1,
            help="The contact of the participation"),
        'assignation_ids' : fields.one2many('groups.group_assignation',
            'participation_id','Assignations',),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context:
            obj.pool.get('ir.sequence').get(cr, uid, 'groups.ref.participation'),
    }

    def groups_in_interval(self, cr, uid, ids, date_from=_MIN_DATETIME, date_to=_MAX_DATETIME, context=None):
        """
        Retorna un diccionari amb claus els identificadors de les participacions
        contingudes en la llista del paràmetre ids. Els valors són una llista de
        diccionaris amb dades sobre els grups amb assignacions per la participació
        identificada amb la clau dins el periode determinat pels paràmetres
        date_from i date_to. La llista de grups es troba ordenada per prioritat
        éssent el grup amb prioritat més alta el quin és primer.
        """
        if not ids: return {}
        res={}
        for id in ids: res[id]=[]
        if ids:
            query="""
            SELECT ga.participation_id,ga.datetime_from,ga.datetime_to,g.id AS gid,g.priority
            FROM groups_group_assignation AS ga
            INNER JOIN groups_group AS g ON ga.group_id=g.id
            WHERE ga.participation_id in %(part_ids)s
                AND ga.limit_from<'%(date_to)s'
                AND ga.limit_to>'%(date_from)s'
            ORDER BY g.priority,ga.datetime_from DESC
            """ % {'part_ids': tuple(ids+[0]),'date_from': date_from, 'date_to': date_to, }
            cr.execute(query)
            for (part_id,datetime_from,datetime_to,group_id,priority) in cr.fetchall():
                if part_id not in res: res[part_id]=[]
                res[part_id]+=[{'group_id': group_id,'datetime_from': datetime_from,'datetime_to': datetime_to,'priority':priority}]
        return res

groups_participation()

class groups_group(osv.osv):
    _name = 'groups.group'

    def _participants(self, cr, uid, ids, field_name, arg, context=None):
        ret={}
        for id in ids: ret[id]=[]
        query='select group_id,participation_id from groups_group_assignation where group_id in %s'
        cr.execute(query, (tuple(ids,),))
        for (gid,pid) in cr.fetchall(): ret[gid].append(pid)
        return ret


    _columns = {
        'name' : fields.char('Name', size=32, required=True, select=1, help="The group name"),
        'parent_ids' : fields.many2many('groups.group','groups_parent_groups_rel','son','father',string='Parents',required=False,
            select=1, help="The parent groups"),
        'assignation_ids' : fields.one2many('groups.group_assignation','group_id','Assignations'),
        'children_ids' : fields.many2many('groups.group','groups_parent_groups_rel','father','son',string='Children',select=1,help="The subgroups of the group"),
        'classification' : fields.char('Classification',size=30,),
        'priority' : fields.integer('Priority'),
        'participants' : fields.function(_participants, method=True, type='one2many',relation='groups.participation'),
        'creation' : fields.integer('Auto creation', required=True,),
    }

    _defaults = {
        'creation': lambda *a: 0,
    }
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct father from groups_parent_groups_rel where son in ('+
                ','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    def _check_classification(self, cr, uid, ids):
        cr.execute("select g.id from groups_group as g inner join groups_parent_groups_rel as gr on g.id=gr.son where classification is not null and g.id in %s group by g.id having count(*)<>1", (tuple(ids),) )
        if cr.fetchall(): return false
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive groups.', ['parent_ids']),
        (_check_classification, 'When a group is member of a classification, it must have only one parent.',['classification'])
    ]

    def _domain_assignations(self, cr, uid, ids, context=None):
        def _inclou_interval_en_llista(llista, interval):
            ret=[]
            (dtf0,dtt0)=interval
            afegit=False
            for (dtf,dtt) in llista:
                if dtt<dtf0:
                    ret.append( (dtf,dtt) )
                elif dtt0<dtf:
                    if not afegit:
                        afegit=True
                        ret.append( (dtf0, dtt0 ) )
                    ret.append( (dtf,dtt) )
                else:
                    dtf0=min(dtf,dtf0)
                    dtt0=max(dtt,dtt0)
            if not afegit: ret.append( (dtf0, dtt0 ) )
            return ret

        ret={}
        domains={}
        for item in self.browse(cr, uid, ids, context={'withoutBlank': False}):
            id=item.id
            ret[id]={}
            if item.parent_ids:
                for parent in item.parent_ids:
                    pid=parent.id
                    if not pid in domains: # per estalviar-nos cercar dominis de pares iguals
                        dict={}
                        for assignation in parent.assignation_ids:
                            key=assignation.participation_id.id
                            if not key in dict: dict[key]=[]
                            dict[key].append( (assignation.datetime_from,assignation.datetime_to) )
                        domains[pid]=dict
                    for (key,value) in domains[pid].items():
                        if key not in ret[id]: ret[id][key]=[]
                        for interval in value:
                            ret[id][key]=_inclou_interval_en_llista(ret[id][key], interval)
            else:
                ret[id]=None # No parent, no domain
        return ret

groups_group()
