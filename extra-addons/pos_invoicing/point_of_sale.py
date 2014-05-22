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
from tools.translate import _
import netsvc
import logging
_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
    _name = "pos.order"
    _inherit = "pos.order"
    
    _columns = {
        'tax_id': fields.char('VAT ID', size=32, required=False, readonly=True),
        'tax_name': fields.char('VAT Name', size=128, readonly=True),
        'seq_number': fields.integer('Sequence Number',readonly=True),
        'invoice_address_id': fields.many2one('res.partner.address', 'Invoice Address', domain="[('partner_id','=',partner_id)]", readonly=True, required=True, states={'draft': [('readonly', False)]}, help="Invoice address for current POS order."),
        'report_name': fields.char('Report Name',size=128,readonly=True),
        'online': fields.related('shop_id','online',type='boolean',string='Shop Online'),
    }
    
    def _default_sale_journal(self, cr, uid, context=None):
        res = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')], limit=1)
        shop = self.pool.get('res.users').browse(cr, uid, uid, context=context).shop_id
        if shop:
            res = [shop.sale_journal_id.id]
        else:
            raise osv.except_osv(_('No shop !'), _("This user does not have a shop associed"))
        return res and res[0] or False
        
    def _default_shop(self, cr, uid, context=None):
        #YT 17/04/2012 Support to multi user in shop
        res = self.pool.get('sale.shop').search(cr, uid, [('user_ids','in',(uid))], context=context)
        return res and res[0] or False
   
    def _default_online(self, cr, uid, context=None):
        res = True
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('user_ids','in',(uid))], context=context)
        res = self.pool.get('sale.shop').read(cr, uid, shop_ids, ['online'], context=context)
        return res and res[0]['online'] or False
 
    #YT 17/04/2012 patch it in the point_of_sale
    _defaults = {
        'name': '/',
        'sale_journal': _default_sale_journal,
        'shop_id': _default_shop,
        'online': _default_online,
    }

    def create_from_ui(self, cr, uid, orders, context=None):
        #_logger.info("orders: %r", orders)
        list = []
        # order :: {'name': 'Order 1329148448062', 'amount_paid': 9.42, 'lines': [[0, 0, {'discount': 0, 'price_unit': 1.46, 'product_id': 124, 'qty': 5}], [0, 0, {'discount': 0, 'price_unit': 0.53, 'product_id': 62, 'qty': 4}]], 'statement_ids': [[0, 0, {'journal_id': 7, 'amount': 9.42, 'name': '2012-02-13 15:54:12', 'account_id': 12, 'statement_id': 21}]], 'amount_tax': 0, 'amount_return': 0, 'amount_total': 9.42}
        order_obj = self.pool.get('pos.order')
        partner_obj = self.pool.get('res.partner')
        for order in orders:
            # get statements out of order because they will be generated with add_payment to ensure
            # the module behavior is the same when using the front-end or the back-end
            statement_ids = order.pop('statement_ids')
            _logger.info('create_from_ui: statement_ids:%s - order.get:%s'%(statement_ids,order.get('statement_ids')))
            
            #YT 1/4/2012 Support to auto adjust the sequence next (possible desync with POS module)
            seq_number = order.get('seq_number')
            if seq_number and order.get('sale_journal'):
                journal = self.pool.get('account.journal').browse(cr,uid, order.get('sale_journal'),context=context)
                sequence_id = journal.sequence_id.id
                sequence_increment = journal.sequence_id.number_increment
                curr_seq = self.pool.get('ir.sequence').next_by_id(cr, uid, sequence_id)
                if order.get('name') != curr_seq:
                    _logger.info("Doesn't are equal the current sequence %s and the sequence push in the pos (%s). It will be adjusted."%(curr_seq, seq_number))
                    self.pool.get('ir.sequence').write(cr, uid, sequence_id, {'number_next': (seq_number+1)}, context=context)
                    _logger.info("Sequence (ID:%s) adjusted from %s to %s + 1"%(sequence_id,curr_seq,seq_number))
            tax_id = order.get('tax_id', False)
            if tax_id:
                partner_ids = partner_obj.search(cr, uid, [('ref','=',tax_id)],context=context)
                if partner_ids:
                    order.update({'partner_id':partner_ids[0]})
                else:
                    partner_id = partner_obj.create(cr, uid,{'name':order.get('tax_name'),'ref':tax_id},context=context)
                    order.update({'partner_id':partner_id})
                    self.pool.get('res.partner.address').create(cr, uid, {'partner_id':partner_id}, context=context)
                    
            order_id = self.create(cr, uid, order, context)
            list.append(order_id)
            # call add_payment; refer to wizard/pos_payment for data structure
            # add_payment launches the 'paid' signal to advance the workflow to the 'paid' state
            data = {
                'journal': statement_ids[0][2]['journal_id'],
                'amount': order['amount_paid'],
                'payment_name': order['name'],
                'payment_date': statement_ids[0][2]['name'],
            }
            order_obj.add_payment(cr, uid, order_id, data, context=context)
        return list

    def add_payment(self, cr, uid, order_id, data, context=None):
        """Create a new payment for the order"""
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        prod_obj = self.pool.get('product.product')
        property_obj = self.pool.get('ir.property')
        curr_c = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        curr_company = curr_c.id
        order = self.browse(cr, uid, order_id, context=context)
        ids_new = []
        args = {
            'amount': data['amount'],
        }
        if 'payment_date' in data.keys():
            args['date'] = data['payment_date']
        args['name'] = order.name
        if data.get('payment_name', False):
            args['name'] = args['name'] + ': ' + data['payment_name']
        account_def = property_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=context)
        args['account_id'] = (order.partner_id and order.partner_id.property_account_receivable \
                             and order.partner_id.property_account_receivable.id) or (account_def and account_def.id) or False
        args['partner_id'] = order.partner_id and order.partner_id.id or None

        if not args['account_id']:
            if not args['partner_id']:
                msg = _('There is no receivable account defined to make payment')
            else:
                msg = _('There is no receivable account defined to make payment for the partner: "%s" (id:%d)') % (order.partner_id.name, order.partner_id.id,)
            raise osv.except_osv(_('Configuration Error !'), msg)

        statement_id = statement_obj.search(cr,uid, [
                                                     ('journal_id', '=', int(data['journal'])),
                                                     ('company_id', '=', curr_company),
                                                     ('user_id', '=', uid),
                                                     ('state', '=', 'open')], context=context)
        if len(statement_id) == 0:
            raise osv.except_osv(_('Error !'), _('You have to open at least one cashbox'))
        if statement_id:
            statement_id = statement_id[0]
        args['statement_id'] = statement_id
        args['pos_statement_id'] = order_id
        args['journal_id'] = int(data['journal'])
        args['type'] = 'customer'
        args['ref'] = order.name
        #YT 12/04/2012 add shop_id
        args['shop_id'] = order.shop_id.id
        #YT 12/04/2012 add partner_id
        args['partner_id'] = order.partner_id and order.partner_id.id
        statement_line_obj.create(cr, uid, args, context=context)
        ids_new.append(statement_id)

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'pos.order', order_id, 'paid', cr)
        wf_service.trg_write(uid, 'pos.order', order_id, cr)

        return statement_id

    def onchange_partner_id(self, cr, uid, ids, part=False, context=None):
        if not part:
            return {'value': {}}
        res = super(pos_order,self).onchange_partner_id(cr, uid, ids, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery', 'invoice'])
        res['value'].update({'invoice_address_id':addr['invoice']})
        return res
        
    def action_invoice(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []

        for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue

            if not order.partner_id:
                raise osv.except_osv(_('Error'), _('Please provide a partner for the sale.'))

            acc = order.partner_id.property_account_receivable.id
            #YT 17/04/2012 add internal_number for not duplicating the sequence of the invoice
            inv = {
                'name': order.name,
                'internal_number': order.name,
                'origin': order.name,
                'account_id': acc,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'currency_id': order.pricelist_id.currency_id.id, # considering partner's sale pricelist's currency
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.partner_id.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(cr, uid, inv, context=context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
            inv_ids.append(inv_id)
            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id = order.partner_id.id,
                                                               fposition_id=order.partner_id.property_account_position.id)['value'])
                if line.product_id.description_sale:
                    inv_line['note'] = line.product_id.description_sale
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name
                inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                    and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                inv_line_ref.create(cr, uid, inv_line, context=context)
            inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
            wf_service.trg_validate(uid, 'pos.order', order.id, 'invoice', cr)

        if not inv_ids: return {}
        
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False
        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_ids and inv_ids[0] or False,
        }

    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        picking_obj = self.pool.get('stock.picking')
        invoice_obj = self.pool.get('account.invoice')
        statement_obj = self.pool.get('account.bank.statement.line')
        for order in self.browse(cr, uid, ids, context=context):
            if order.state not in ('paid','invoiced'):
                continue
            if order.picking_id:
                picking_obj.action_cancel(cr,uid,[order.picking_id.id],context=context)
            if order.invoice_id:
                invoice_obj.action_cancel(cr,uid,[order.invoice_id.id])
            for statement in order.statement_ids:
                if statement.statement_id.state in ('confirm'):
                    raise osv.except_osv('Error', 'The statement %s must be in open state.'%(statement.statement_id.name))
                else:
                    statement_obj.unlink(cr,uid,[statement.id], context=context)
            self.write(cr,uid,[order.id],{'state':'cancel'},context=context)
            
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'pos.order', order.id, 'cancel', cr)
            wf_service.trg_write(uid, 'pos.order', order.id, cr)
        return True

pos_order()

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'birthday':fields.date('Birthday'),
        'events_ids': fields.one2many('res.partner.events','partner_event_id','Important Dates'),
        }
res_partner()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
