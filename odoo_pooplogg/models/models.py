# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class customer_property(models.Model):
    _name = 'customer.property'
    _description = 'Customer Property'
    
    property_name = fields.Char(string="Name")
    property_id = fields.Char(string="Property ID")
    address = fields.Char(string="Address")
    zone_name = fields.Char(string="Zone Name")
    sewage_records = fields.Char(string="Sewage Records")
    owner_id = fields.Many2one('res.partner', string="Property Owner")
    customer_id = fields.Char(string="Customer ID")
    manager_id = fields.Many2one('res.partner', string="Property Manager")
    
    @api.model
    def assign_owner(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            owner = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
            if owner:
                rec.owner_id = owner.id
            
class property_zone(models.Model):
    _name = 'property.zone'
    _description = 'Property Zone'
    
    name = fields.Char(string="Name")
    
class evacuation_category(models.Model):
    _name = 'evacuation.category'
    _description = 'Evacuation Category'
    
    name = fields.Char(string="Name")
        
class customer_wallet(models.Model):
    _name = 'customer.wallet'
    _description = 'Customer Wallet'
    
    date = fields.Date(
        string='Date',
        required=True,
        index=True,
        readonly=True,
        copy=False,
        default=fields.Date.context_today
    )
    type = fields.Selection([('credit', 'CREDIT'), ('debit', 'DEBIT')], 'Type')
    amount = fields.Float(string="Amount")
    payment_id = fields.Char(string="Payment")
    customer = fields.Many2one('res.partner', string="Customer")
    customer_id = fields.Char(string="Customer ID")
    
    @api.model
    def assign_customer(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            customer = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
            if customer:
                rec.customer = customer.id   
            
            
class partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    customer_id = fields.Char(string="PAS ID")
    bank_code = fields.Char(string = "Bank Code")
    partner_id = fields.Many2one('res.partner', 'Account Holder', ondelete='cascade', index=True, domain=['|', ('is_company', '=', True), ('parent_id', '=', False)], required=False)
    
    @api.model
    def assign_bank(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if (rec.customer_id):
                customer = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
                rec.partner_id = customer.id
            if (rec.bank_code):
                bank = self.env['res.bank'].search([('bic', '=', rec.bank_code)])
                rec.bank_id = bank.id
            

class pooplogg_customer(models.Model):
    _inherit = 'res.partner'
    
    properties = fields.One2many('customer.property', 'owner_id', store=True, string="Properties")
    transactions = fields.One2many('customer.wallet', 'customer', store=True, string="Wallet Transactions")
    truck_id = fields.Char()
    customer_id = fields.Char(string="PAS ID")
    category = fields.Selection([('customer', 'Customer'), ('partner', 'Partner'), ('manager', 'Manager')], 'Category')
    driver_id = fields.Char()
    wallet = fields.Float(string="Wallet Balance")
    
    @api.model
    def update_partner(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if (rec.driver_id and rec.customer_id):
                partner = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
                rec.partner_id = partner.id
            if (rec.truck_id and rec.customer_id):
                partner = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
                rec.partner_id = partner.id

    @api.model
    def set_company(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if(rec.customer_id):
                tag = self.env['res.partner.category'].search([('name','=',record.category)])
                if tag:
                    rec.write({'category_id':[(tag.id)]})
                rec.company_id = 2
                if rec.category == 'customer':
                    rec.customer_rank = 1
                else:
                    rec.supplier_rank = 1
                
    @api.onchange('category')
    def customer_categ(self):
        for record in self:
            if (record.category):
                tag = self.env['res.partner.category'].search([('name','=',record.category)])
                if tag:
                    record.write({'category_id':[(tag.id)]})
    
    @api.model
    def get_properties(self): 
        properties = []
        domain=[('owner_id', '=', self.id)]
        property = self.env['customer.property'].search(domain)
        for rec in property:
            properties.append((0,0, {'property_name':rec.property_name, 'property_id':rec.property_id, 'address':rec.address, 'zone_name':rec.zone_name, 'owner_id': rec.id, 'sewage_records':rec.sewage_records, 'customer_id':rec.customer_id}))
        self.update({'properties': properties})
        
    @api.model
    def get_wallet_transactions(self): 
        wallet = []
        domain=[('customer', '=', self.id)]
        transactions = self.env['customer.wallet'].search(domain)
        for rec in transactions:
            wallet.append((0,0, {'date':rec.date, 'type':rec.type, 'amount':rec.amount, 'payment_id':rec.payment_id}))
        self.update({'transactions': wallet})

class partner_price(models.Model):
    _inherit = 'product.product'
    
    partner_price = fields.Float(string="Partner Price")
    zone = fields.Many2one('property.zone', string="Location Zone")
    evac_categ = fields.Many2one('evacuation.category', string="Evacuation Category")
    
class account_journal(models.Model):
    _inherit = 'account.journal'
    
    payment_method = fields.Selection([('CASH', 'CASH'), ('CARD', 'CARD'), ('WALLET', 'WALLET')], 'Payment Method')

class payment(models.Model):
    _inherit = 'account.payment'
    
    truck_owner_id = fields.Char()
    truck_owner = fields.Many2one('res.partner', string="Truck Owner")
    customer_id = fields.Char()
    truck_id = fields.Char()
    property_id = fields.Char()
    product_type = fields.Char()
    evac_category = fields.Char()
    default_code = fields.Char()
    payment_method = fields.Char()
    addon = fields.Char()
    addon_amount = fields.Float()
    sewage_volume = fields.Float()
    discount = fields.Float()
    
    @api.model
    def update_payment(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if(rec.truck_owner_id and rec.customer_id):
                rec.payment_type = 'inbound'
                rec.partner_type = 'customer'
                payment_journal = self.env['account.journal'].search([('payment_method', '=', rec.payment_method)])
                if payment_journal:
                    rec.journal_id = payment_journal.id
                customer = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
                truck_owner = self.env['res.partner'].search([('customer_id', '=', rec.truck_owner_id)])
                if customer:
                    rec.partner_id = customer.id
                if truck_owner:
                    rec.truck_owner = truck_owner.id
                
            if (rec.customer_id and rec.product_type == 'WALLET'):
                rec.payment_type = 'inbound'
                rec.partner_type = 'customer'
                payment_journal = self.env['account.journal'].search([('payment_method', '=', rec.payment_method)])
                if payment_journal:
                    rec.journal_id = payment_journal.id
                customer = self.env['res.partner'].search([('customer_id', '=', rec.customer_id)])
                if customer:
                    rec.partner_id = customer.id
                
    @api.model
    def create_invoice(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if(rec.truck_owner_id and rec.customer_id):
                category = self.env['product.category'].search([('name', '=', rec.product_type)])
                evac_categ = self.env['evacuation.category'].search([('name', '=', rec.evac_category)])
                product = self.env['product.product'].search([('categ_id', '=', category.id),('default_code','=', rec.default_code),('evac_categ', '=', evac_categ.id)])
                journal = self.env['account.journal'].search([('company_id', '=', 2), ('code', '=', 'INV')])
                invoice_line_ids = []
                invoice_line_ids.append((0,0,{'product_id':product.id, 'account_id':product.categ_id.property_account_income_categ_id.id, 'price_unit':product.lst_price, 'quantity':1, 'discount':rec.discount}))
                
                if (rec.addon):
                    invoice_line_ids.append((0,0,{'name':rec.addon, 'account_id':product.categ_id.property_account_income_categ_id.id, 'price_unit':rec.addon_amount, 'quantity':1}))
                
                vals = {'partner_id':rec.partner_id, 'journal_id':journal.id,'company_id':2, 'move_type':'out_invoice', 'invoice_line_ids':invoice_line_ids}
                invoice = self.env['account.move'].create(vals)
                invoice.action_post()
                rec.action_post()
                
            if(rec.customer_id and rec.product_type == 'WALLET'):
                category = self.env['product.category'].search([('name', '=', rec.product_type)])
                product = self.env['product.product'].search([('categ_id', '=', category.id)])
                journal = self.env['account.journal'].search([('company_id', '=', 2), ('code', '=', 'INV')])
                invoice_line_ids = []
                invoice_line_ids.append((0,0,{'product_id':product.id, 'account_id':product.categ_id.property_account_income_categ_id.id, 'price_unit':rec.amount, 'quantity':1}))
                
                vals = {'partner_id':rec.partner_id, 'journal_id':journal.id,'company_id':2, 'move_type':'out_invoice', 'invoice_line_ids':invoice_line_ids}
                invoice = self.env['account.move'].create(vals)
                invoice.action_post()
                rec.action_post()
                
#     Wallet Transactions            
    @api.model
    def fund_wallet(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if(rec.customer_id and rec.product_type == 'WALLET'):
                wallet_vals = {'customer_id':rec.customer_id, 'type':'credit','amount':rec.amount, 'payment_id':rec.ref}
                self.env['customer.wallet'].create(wallet_vals)
                rec.partner_id.wallet += rec.amount
                
    @api.model
    def deduct_wallet(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if(rec.truck_owner_id and rec.customer_id and rec.payment_method == 'WALLET'):
                wallet_vals = {'customer_id':rec.customer_id, 'type':'debit','amount':rec.amount, 'payment_id':rec.ref}
                self.env['customer.wallet'].create(wallet_vals)
                rec.partner_id.wallet -= rec.amount
                
        
#     Payment Split between partners         
    @api.model
    def partner_split(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if(rec.truck_owner_id and rec.customer_id):
                truck_owner = self.env['res.partner'].search([('customer_id', '=', rec.truck_owner_id)])
                category = self.env['product.category'].search([('name', '=', rec.product_type)])
                evac_categ = self.env['evacuation.category'].search([('name', '=', rec.evac_category)])
                product = self.env['product.product'].search([('categ_id', '=', category.id),('default_code','=', rec.default_code),('evac_categ', '=', evac_categ.id)])
                vat = round((product.lst_price * 0.075), 2)
                net = product.lst_price - vat
                partner_earning = product.partner_price
                partner_account = truck_owner.property_account_payable_id.id
                loggycraft = self.env['res.partner'].search([('name', '=', 'Loggykraft')])    
                loggycraft_earning = round(((net - partner_earning) * 0.4), 2)
                loggycraft_account = loggycraft.property_account_payable_id.id
                vat_account = self.env['account.account'].search([('name', '=', 'VAT Payable')])
                
                line_ids = []
                line_ids.append((0,0,{'account_id':partner_account, 'partner_id':rec.truck_owner.id, 'credit':partner_earning}))
                line_ids.append((0,0,{'account_id':loggycraft_account, 'partner_id':loggycraft.id, 'credit':loggycraft_earning}))
                line_ids.append((0,0,{'account_id':vat_account.id,  'credit':vat}))
                
                property = self.env['customer.property'].search([('property_id', '=', rec.property_id)])
                
                if (property.manager_id):
                    manager = property.manager_id.id
                    manager_account = property.manager_id.property_account_payable_id.id
                    manager_earning = round(((net - partner_earning) * 0.02), 2)
                    expense = partner_earning + loggycraft_earning + manager_earning + vat                                
                    line_ids.append((0,0,{'account_id':manager_account, 'partner_id':manager, 'credit':manager_earning}))
                
                else:
                   expense = partner_earning + loggycraft_earning + vat
                
                expense_account = product.categ_id.property_account_expense_categ_id.id
                line_ids.append((0,0,{'account_id':expense_account, 'debit':expense}))
                journal = self.env['account.journal'].search([('company_id', '=', 2), ('code', '=', 'MISC')])
                vals = {'ref':rec.ref + " - partners' share", 'company_id':2, 'journal_id':journal.id, 'move_type':'entry', 'line_ids':line_ids}
                _logger.info(vals)
                journal = self.env['account.move'].create(vals)
                journal.action_post()
        
    
