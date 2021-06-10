# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partner_price(models.Model):
    _inherit = 'product.product'
    
    partner_price = fields.Float(string="Partner Price")

class payment(models.Model):
    _inherit = 'account.payment'
    
    product_id = fields.Many2one('product.product', string="Product")
    truck_owner = fields.Many2one('res.partner', string="Truck Owner")
    manager = fields.Many2one('res.partner', string="Manager")
    
    
    @api.model
    def create_invoice(self, name):
        record = self.search([('name', '=', name)])
        for rec in record:
            if(rec.payment_type == 'inbound' and rec.truck_owner and rec.product_id):
                product = rec.product_id
                journal = self.env['account.journal'].search([('company_id', '=', rec.company_id.id), ('code', '=', 'INV')])
                invoice_line_ids = []
                invoice_line_ids.append((0,0,{'product_id':product.id, 'account_id':rec.product_id.categ_id.property_account_income_categ_id.id, 'price_unit':rec.product_id.lst_price, 'quantity':1}))
                vals = {'partner_id':rec.partner_id.id, 'journal_id':journal.id,'company_id':rec.company_id.id, 'move_type':'out_invoice', 'invoice_line_ids':invoice_line_ids}
                invoice = self.env['account.move'].create(vals)
                invoice.action_post()
                rec.action_post()
                
                vat = round((product.lst_price * 0.75), 2)
                net = product.lst_price - vat
                partner = rec.truck_owner.id
                partner_account = rec.truck_owner.property_account_payable_id.id
                partner_earning = rec.product_id.partner_price - round((vat * 0.3), 2)
                loggycraft = self.env['res.partner'].search([('name', '=', 'Loggycraft')])
                loggycraft_account = loggycraft.property_account_payable_id.id           
                loggycraft_earning = round((net * 0.3), 2)
                expense_account = rec.product_id.categ_id.property_account_expense_categ_id.id
                
                line_ids = []
                line_ids.append((0,0,{'account_id':partner_account, 'partner_id':partner, 'credit':partner_earning}))
                line_ids.append((0,0,{'account_id':loggycraft_account, 'partner_id':loggycraft, 'credit':loggycraft_earning}))
#                 line_ids.append((0,0,{'account_id':vat_account,  'credit':vat}))
                
                if (rec.manager){
                    manager = rec.manager.id
                    manager_account = rec.manager.property_account_payable_id.id
                    manager_earning = round((net * 0.02), 2)
                    expense = partner_earning + loggycraft_earning + manager_earning + vat                                
                    line_ids.append((0,0,{'account_id':manager_account, 'partner_id':manager, 'credit':manager_earning}))   
                }
                
                else {
                   expense = partner_earning + loggycraft_earning + vat 
                }
                
                line_ids.append((0,0,{'account_id':expense_account, 'debit':expense}))
                vals = {'ref':invoice.name + " - partners' share" + , 'company_id':rec.company_id.id, 'move_type':'entry', 'line_ids':line_ids}
                journal = self.create(vals)
                journal.action_post()
    
