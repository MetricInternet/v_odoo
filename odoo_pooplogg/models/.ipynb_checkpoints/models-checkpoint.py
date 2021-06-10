# -*- coding: utf-8 -*-

from odoo import models, fields, api


class payment(models.Model):
    _inherit = 'account.payment'
    
    product_id = fields.Many2one('product.product', string="Product")
    truck_owner = fields.Many2one('res.partner', string="Truck Owner")
    manager = fields.Many2one('res.partner', string="Manager")
    
