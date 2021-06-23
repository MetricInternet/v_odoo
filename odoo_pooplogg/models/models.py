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
    address = fields.Char(string="Address")
    zone_name = fields.Char(string="Zone Name")
    sewage_records = fields.Char(string="Sewage Tank Records")
    owner_id = fields.Many2one('res.partner', string="Property Owner")
    customer_id = fields.Char()

class pooplogg_customer(models.Model):
    _inherit = 'res.partner'
    
    properties = fields.One2many('customer.property', 'owner_id', store=True, string="Properties")
    truck_id = fields.Char()
    customer_id = fields.Char()
    category = fields.Selection([('customer', 'Customer'), ('partner', 'Partner')], 'Category')
    driver_id = fields.Char()
    
    @api.model
    def get_properties(self): 
        properties = []
        domain=[('owner_id', '=', self.id)]
        property = self.env['customer.property'].search(domain)
        for rec in property:
            properties.append((0,0, {'property_name':rec.property_name, 'address':rec.address, 'zone_name':rec.zone_name, 'owner_id': rec.id, 'sewage_records':rec.sewage_records, 'customer_id':rec.customer_id}))
        self.update({'properties': properties})

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
                
    @api.model
    def create_journal(self, name):
        record = self.search([('name', '=', name)])
        for rec in record:
            if(rec.payment_type == 'inbound' and rec.truck_owner and rec.product_id):
                product = rec.product_id
                vat = round((product.lst_price * 0.075), 2)
                net = product.lst_price - vat
                partner_earning = rec.product_id.partner_price
                partner_account = rec.truck_owner.property_account_payable_id.id
                loggycraft = self.env['res.partner'].search([('name', '=', 'Loggycraft')])    
                loggycraft_earning = round(((net - partner_earning) * 0.3), 2)
                loggycraft_account = loggycraft.property_account_payable_id.id
                vat_account = self.env['account.account'].search([('name', '=', 'VAT Payable')])
                
                line_ids = []
                line_ids.append((0,0,{'account_id':450, 'partner_id':rec.truck_owner.id, 'credit':partner_earning}))
                line_ids.append((0,0,{'account_id':450, 'partner_id':loggycraft.id, 'credit':loggycraft_earning}))
                line_ids.append((0,0,{'account_id':vat_account.id,  'credit':vat}))
                
                if (rec.manager):
                    manager = rec.manager.id
                    manager_account = rec.manager.property_account_payable_id.id
                    manager_earning = round(((net - partner_earning) * 0.02), 2)
                    expense = partner_earning + loggycraft_earning + manager_earning + vat                                
                    line_ids.append((0,0,{'account_id':450, 'partner_id':manager, 'credit':manager_earning}))
                
                else:
                   expense = partner_earning + loggycraft_earning + vat
                
                expense_account = rec.product_id.categ_id.property_account_expense_categ_id.id
                line_ids.append((0,0,{'account_id':454, 'debit':expense}))
                journal = self.env['account.journal'].search([('company_id', '=', rec.company_id.id), ('code', '=', 'MISC')])
                vals = {'ref':rec.ref + " - partners' share", 'company_id':rec.company_id.id, 'journal_id':journal.id, 'move_type':'entry', 'line_ids':line_ids}
                _logger.info(vals)
                journal = self.env['account.move'].create(vals)
                journal.action_post()
    
