# -*- coding: utf-8 -*-

from odoo import models, fields, api


class vendor_identifier(models.Model):
    _inherit = 'res.partner'

    unique_id = fields.Char(string="Unique ID")
    
    @api.model
    def generate_id(self, id):
        record = self.search([('id', '=', id)])
        for rec in record:
            if not rec.unique_id:
                seq = env['ir.sequence'].next_by_code('partner.sequence')
                rec.write({'unique_id':seq})
        
        
        