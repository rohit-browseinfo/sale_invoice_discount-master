# -*- coding: utf-8 -*-
##############################################################################
#
#    Sales and Account Invoice Discount Management
#    Copyright (C) 2004-2010 BrowseInfo(<http://www.browseinfo.in>).
#    $author:BrowseInfo
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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'discount_amt':0.0,
            }
            val1 = 0.0
            for line in invoice.invoice_line:
                val1 += line.price_subtotal
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            disc_amt = invoice.discount_amount
            disc_method = invoice.discount_method
            new_amt = 0.0
            new_amt = val1 * disc_amt / 100

            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed'] - new_amt
            self.write(cr, uid, ids, {'discount_amt': new_amt})
        return res
 
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
  
    _columns = {
        'discount_method': fields.selection([('fix', 'Fixed'),('per', 'Percentage')], 'Discount Method'),
        'discount_amount': fields.float('Discount Amount'),
        'discount_amt': fields.float('- Discount', readonly=True,),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','discount_amount'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
      }

    def discount_set(self, cr, uid, ids, context=None):
        amount_total = self.browse(cr, uid, ids, context=context)[0].amount_untaxed
        disc_amt = self.browse(cr, uid, ids, context=context)[0].discount_amount
        print"==============disc_amt",disc_amt
        disc_methd = self.browse(cr, uid, ids, context=context)[0].discount_method
        print "disc_method",disc_methd
        new_amt = 0.0
        new_amtt = 0.0
        if disc_amt:
            if disc_methd == 'per':
                new_amtt = amount_total * disc_amt / 100
                new_amt = amount_total * (1 - (disc_amt or 0.0) / 100.0)
                self.write(cr, uid, ids, {'discount_amt': new_amtt,'amount_total':new_amt})
            elif disc_methd == 'fix':
                new_amtt = disc_amt 
                new_amt = amount_total - disc_amt 
                self.write(cr, uid, ids, {'discount_amt': new_amtt,'amount_total':new_amt})
            else :
                self.write(cr, uid, ids, {'discount_amt': new_amtt,'amount_total':amount_total}) 
            return True

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
